from slurm.runner import *

def test_prepare_apptainer():
    apptainer_invocation = '''
apptainer exec \
--bind /gscratch \
--overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
/gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
"{{cmd}}"'''

    script = '''
{{run_foo}}

{{run_bar}}'''

    assert prepare_apptainer(script, apptainer_invocation).strip() == '''
apptainer exec \
--bind /gscratch \
--overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
/gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
"{{foo}}"


apptainer exec \
--bind /gscratch \
--overlay /gscratch/spe/${USER}/apptainer_images/conda-overlay.img:ro \
/gscratch/spe/${USER}/apptainer_images/hyak-container.sif /bin/bash -l -c \
"{{bar}}"'''.strip()


def test_prepare_commands():
    script = '''
#!/bin/bash
#SBATCH --account=stf
#SBATCH --partition=ckpt
#SBATCH --nodes=1

{{foo}}

exit 0
'''

    assert prepare_commands(script, {"foo": "{bar}/{baz}"}).strip() == '''
#!/bin/bash
#SBATCH --account=stf
#SBATCH --partition=ckpt
#SBATCH --nodes=1

{bar}/{baz}

exit 0
'''.strip()
