import subprocess
import os
import tempfile
import time
import threading
import queue
import io
import yaml
import argparse

from rich.progress import Progress, BarColumn, TextColumn, TaskID, TimeRemainingColumn
from typing import *

import h5py
import hdf5plugin

from zernikegrams.utils import log_config as logging
logger = logging.getLogger(__name__)


################################################################################
# Taken from https://github.com/StatPhysBio/statphysbio-wiki/blob/main/hyak/utils.py
################################################################################
def get_jobs(watchers: List[queue.Queue], sleep: int = 10) -> None:
    while len(watchers) > 0:
        # Get a list of all jobids, nodes, and num cpus for the jobs you currently are running.
        # Example output:
        # JOBID       MIN_CP
        # 17941698      2
        # 17938396     40
        squeue_output = (
            subprocess.run(
                ["squeue", '-o "%.18i %.6c "', "--me"],
                check=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .replace('"', "")
            .strip()
            .split("\n")[1:]
        )


        for q in watchers:
            q.put(squeue_output)

        time.sleep(sleep)
    logger.info("watcher thread shutting down")


################################################################################
# Taken from https://github.com/StatPhysBio/statphysbio-wiki/blob/main/hyak/utils.py
################################################################################
def in_queue(jobid: str, output: str) -> bool:
    """
    Given a jobid, returns True if job is in slurm queue,
    False otherwise
    """
    for line in output:
        line = line.split()

        # check for array jobs
        query = line[0]
        if "_" in query:
            query = query.split("_")[0]

        if query == jobid:
            return True

    return False


def submit_job(script: str) -> str:
    """
    Submits a slurm script and returns
    the jobid
    """
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(script.encode("utf-8"))
        tmp.flush()

        output = (
            subprocess.run(
                ["sbatch", tmp.name], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE
            )
            .stdout.decode("utf-8")
            .strip()
        )

        jobid = output.split()[-1]
        return jobid


def await_job(jobid: str, jobs_queue: queue.Queue) -> None:
    """
    Blocks while jobid is in the queue
    sleep: seconds between checking if job is in queue
    """
    # allow slurm to put job in queue
    time.sleep(5)
    while True:
        output = jobs_queue.get()
        if not in_queue(jobid, output):
            return


def run_job(script: str, result_queue: queue.Queue, jobs_queue: queue.Queue) -> None:
    jobid = submit_job(script)
    await_job(jobid, jobs_queue)
    result_queue.put(jobid)


def submit_and_await_batch(scripts: List[str], name: str = None) -> None:
    """
    Given a list of scripts to run, submits all and
    blocks until they finish. Has a nice progress bar, too.
    """
    if name is None:
        name = "Running jobs"

    num_jobs = len(scripts)

    result_queue = queue.Queue()
    squeue_consumers = []
    threads = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("[progress.completed]{task.completed}/{task.total} jobs"),
        TimeRemainingColumn(),
    ) as progress:

        task: TaskID = progress.add_task(f"[green]{name}", total=num_jobs)

        for script in scripts:
            squueu_consumer = queue.Queue()
            t = threading.Thread(target=run_job, args=(script, result_queue, squueu_consumer))
            t.start()
            threads.append(t)
            squeue_consumers.append(squueu_consumer)

        logger.info("Submitted all jobs")

        squeue_watcher = threading.Thread(target=get_jobs, args=(squeue_consumers,), daemon=True)
        squeue_watcher.start()

        completed_jobs = 0
        while completed_jobs < num_jobs:
            jobid = result_queue.get()
            progress.update(task, advance=1)
            completed_jobs += 1

        for t in threads[:-1]:
            t.join()
        
        # kill squeue_watcher
        for i in range(len(squeue_consumers)):
            squeue_consumers.pop()

        

def prepare_apptainer(script: str, apptainer_invocation, prefix: str = "run_") -> str:
    """
    Given a script str and an apptainer_invocation str that contains {{cmd}}
    Performs string replacement as follows:

    # apptainer_invocation = 

    '''apptainer exec \
    --bind /gscratch \
    --overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
    /gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
    "{{cmd}}"
    '''

    script = '''
    {{run_foo}}

    {{run_bar}}
    
    {{run_baz}}
    '''

    returns

    '''
    apptainer exec \
    --bind /gscratch \
    --overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
    /gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
    "{{foo}}"

        apptainer exec \
    --bind /gscratch \
    --overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
    /gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
    "{{bar}}"

        apptainer exec \
    --bind /gscratch \
    --overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
    /gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
    "{{baz}}"
    '''

    Note that the resulting commands are still wrapped in {{}}. 
    This is meant to be used immediately before `prepare_commands`
    """
    if r"{{cmd}}" not in apptainer_invocation:
        raise ValueError(r"Apptainer invocation must have {{cmd}}")

    with io.StringIO() as buffer:
        for line in script.split("\n"):
            if line.count(f"{{{prefix}") > 1:
                raise ValueError(
                    "Cannot perform string substitution on line with multiple {{", line
                )
            if line.count(f"{{{prefix}") > 0:
                left = line.find(f"{{{prefix}") + len(prefix) + 1
                right = line.find("}}")
                sub = line[left:right]
                line = apptainer_invocation.replace("{{cmd}}", "{{" + sub + "}}")
            buffer.write(f"{line}\n")

        return buffer.getvalue()


def prepare_commands(script: str, replacement_dict: Dict[str, str]) -> str:
    """
    Given a script str and a replacement_dict, replaces
    {{keys}} with values.

    Example:

    script = '''
    #!/bin/bash
    #SBATCH --account=stf
    #SBATCH --partition=ckpt
    #SBATCH --nodes=1

    {{foo}}

    exit 0
    '''

    and replacement_dict = {'foo': 'echo "hello world"'}

    then the return value is '''
    #!/bin/bash
    #SBATCH --account=stf
    #SBATCH --partition=ckpt
    #SBATCH --nodes=1

    echo "hello world"

    exit 0
    '''
    """
    for key, value in replacement_dict.items():
        script = script.replace("{{" + str(key) + "}}", str(value))

    if "{{" in script:
        raise ValueError("Some substitutions failed", script)

    return script


def count_lines(path: str) -> int:
    """
    returns the number of lines in the file
    """
    with open(path, "r") as f:
        return sum([1 for line in f.readlines()])


def structural_info(config: Dict) -> Tuple[List[str], Dict[str, List[str]]]:
    script = open(config["structural-info"]["template"], "r").read()
    structural_info_scripts = []

    file_path = os.path.join(
        config["structural-info"]["pdb_ids_path"], config["structural-info"]["pdb_ids"]
    )

    to_combine = {}
    for split in config["scripts"]["splits"]:
        i = 0
        file_idxs = config["scripts"]["splits"][split]["file_idx"]
        for file_idx in file_idxs:
            file = prepare_commands(file_path, {"split": split, "file_idx": file_idx})
            n_lines = count_lines(file)

            combine_key = f"{file.removesuffix('.txt')}_struct_NoiseNone.hdf5"
            combine_key = os.path.join(f"{config['scripts']['tmp_path']}", os.path.basename(combine_key))
            to_combine[combine_key] = []

            chunk_size = config["structural-info"]["chunk_size"]
            for line_idx in range(1, n_lines + 1, chunk_size):
                replacement_dict = (
                    config["structural-info"]
                    | config["sbatch"]
                    | config["scripts"]
                    | config["scripts"]["commands"]
                    | {
                        "split": split,
                        "file_idx": file_idx,
                        "line_idx": line_idx,
                        "i": i,
                    }
                )

                structural_info_scripts.append(
                    prepare_commands(
                        prepare_apptainer(
                            script,
                            apptainer_invocation=config["apptainer"]["invocation"],
                            prefix=config["scripts"]["prefix"]
                        ),
                        replacement_dict
                    )
                )

                to_combine[combine_key].append(f"{config['scripts']['tmp_path']}/{split}_struct_{file_idx}_{line_idx}.hdf5")
                i += 1
    
    return structural_info_scripts, to_combine


def combine_hdf5s(config: Dict, to_combine: Dict[str, List[str]]) -> None:
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("[progress.completed]{task.completed}/{task.total} jobs"),
        TimeRemainingColumn(),
    ) as progress:

        task: TaskID = progress.add_task("[green]combining structural info files", total=len(to_combine))

        for consumer, producers in to_combine.items():
            N = 0
            for producer in producers:
                with h5py.File(producer, "r") as f_in:
                    dt_data = f_in["data"].dtype
                    N += len(f_in["data"])

            with h5py.File(consumer, "w") as f_out:
                f_out.create_dataset("data", (N,), dtype=dt_data)
                n = 0
                for producer in producers:
                    with h5py.File(producer, "r") as f_in:
                        length = len(f_in["data"])
                        f_out["data"][n : n + length] = f_in["data"][:]
                        n += length

            progress.update(task, advance=1)


def neighborhoods_and_zernikegrams(config: Dict) -> List[str]:
    script = open(config["preprocessing"]["template"], "r").read()
    zgram_scripts = []

    i = 0
    for split in config["scripts"]["splits"]:
        file_idxs = config["scripts"]["splits"][split]["file_idx"]
        for file_idx in file_idxs:
            for seed in config["add-noise"]["seeds"]:
                replacement_dict = (
                    config["sbatch"]
                    | config["scripts"]
                    | config["scripts"]["commands"]
                    | {
                        "split": split,
                        "file_idx": file_idx,
                        "seed": seed,
                        "i": i
                    }
                )

                zgram_scripts.append(
                    prepare_commands(
                        prepare_apptainer(
                            script,
                            apptainer_invocation=config["apptainer"]["invocation"],
                            prefix=config["scripts"]["prefix"]
                        ),
                        replacement_dict
                    )
                )
                i += 1

    return zgram_scripts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    for path in (config["scripts"]["tmp_path"], config["scripts"]["final_path"]):
        if not os.path.exists(path):
            os.makedirs(path)

    structural_info_scripts, to_combine = structural_info(config)
    submit_and_await_batch(structural_info_scripts, name="structural info")
    
    combine_hdf5s(config, to_combine)

    zgrams_scripts = neighborhoods_and_zernikegrams(config)
    submit_and_await_batch(zgrams_scripts, name="neighborhoods and zernikegrams")


if __name__ == "__main__":
    main()
