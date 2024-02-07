import argparse
import h5py
import hdf5plugin
import os
import sqlitedict
import time

from typing import (
    List,
    Tuple,
)
from rich.progress import Progress

import numpy as np

from src.utils import log_config as logging
from src.utils.pdb_lists import (
    pdb_list_from_dir,
    pdb_list_from_foldcomp,
)
from src.preprocessors.pdbs import (
    PDBPreprocessor,
    FoldCompPreprocessor,
)
from src.structural_info.structural_info_core import (
    get_structural_info_from_protein,
    pad_structural_info,
)

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hdf5_out",
        type=str,
        help="Output hdf5 filename, where structural info will be stored.",
        required=True,
    )
    parser.add_argument(
        "--output_dataset_name",
        type=str,
        help='Name of the dataset within output_hdf5 where the structural information will be saved. We recommend keeping this set to simply "data".',
        default="data",
    )
    parser.add_argument(
        "--pdb_list_file",
        type=str,
        help="Path to file containing list of PDB files of interest, one per row. Required if --foldcomp is not set",
    )
    parser.add_argument(
        "--pdb_dir",
        type=str,
        help="directory of pdb files. Required if --foldcomp is not set",
    )
    parser.add_argument(
        "--foldcomp",
        type=str,
        help="Path to foldcomp file containing compressed PDBs. Required if --pdb_dir and --pdb_list_file not set",
    )
    parser.add_argument(
        "--parallelism", type=int, help="Maximum number of CPU cores to use.", default=4
    )
    parser.add_argument(
        "--max_atoms",
        type=int,
        help="max number of atoms per protein, for padding purposes",
        default=200000,
    )
    parser.add_argument("--logging", type=str, help="logging level", default="INFO")
    parser.add_argument(
        "--angle_db", type=str, help="path to chi angle database", default=None
    )
    parser.add_argument(
        "--vec_db", type=str, help="path to normal vector database", default=None
    )
    parser.add_argument(
        "--SASA",
        action="store_true",
        default=False,
        help="If present, SASAs are calculated for each atom.",
    )
    parser.add_argument(
        "--charge",
        action="store_true",
        default=False,
        help="If present, charges are calculated for each atom.",
    )

    args = parser.parse_args()
    if args.pdb_dir is None and args.foldcomp is None:
        msg = "pdb_dir or foldcomp must be set"
        logger.exception(msg)
        raise ValueError(msg)

    args.input_path = args.foldcomp if args.foldcomp is not None else args.pdb_dir
    return args


def get_structural_info_from_dataset(
    input_path: str,
    pdb_list: List[str],
    max_atoms: int,
    hdf5_out: str,
    output_dataset_name: str,
    parallelism: int,
    angle_db: str = None,
    vec_db: str = None,
    SASA: bool = True,
    charge: bool = True,
) -> None:
    """
    Parallel processing of PDBs into structural info

    Parameters
    ---------
    inputs:
        either 1)
            pdb_dir : str
                Path where the pdb files are stored
        or 2)
            foldcomp: str
                path to foldcomp file with compressed PDBs
    pdb_list: List of PDBs to processes
    max_atoms : int
        Max number of atoms in a protein for padding purposes
    hdf5_out : str
        Path to hdf5 file to write
    parallelism : int
        Number of workers to use
    angle_db : str | None
        If set, path to sqlite db to store chi angles.
        Keys will be residue IDs and values will be up to four chi angles
    vec_db : str | None
        If set, path to sqlite db to store normal vectors.
        Keys will be residue IDs and values will be up to four normal vectors
    SASA: bool
        Whether or not to calculate SASAs
    charge: bool
        Whether or not to calculate charges
    """
    if os.path.isdir(input_path):
        pdb_dir = input_path

        pdb_list_from_dir = []
        for file in os.listdir(pdb_dir):
            if file.endswith(".pdb"):
                pdb = file.removesuffix(".pdb")
                pdb_list_from_dir.append(pdb)

        # filter out pdbs that are not in the directory
        pdb_list = list(set(pdb_list) & set(pdb_list_from_dir))

        processor = PDBPreprocessor(pdb_list, pdb_dir)

    else:
        processor = FoldCompPreprocessor(pdb_list, input_path)

    L = np.max([processor.pdb_name_length, 5])
    logger.info(f"Maximum pdb name L = {L}")

    dt_arr = [
        ("pdb", f"S{L}", ()),
        ("atom_names", "S4", (max_atoms)),
        ("elements", "S2", (max_atoms)),
        ("res_ids", f"S{L}", (max_atoms, 6)),
        ("coords", "f4", (max_atoms, 3)),
    ]
    if SASA:
        dt_arr.append(("SASAs", "f4", (max_atoms)))
    if charge:
        dt_arr.append(("charges", "f4", (max_atoms)))
    dt = np.dtype(dt_arr)

    with h5py.File(hdf5_out, "w") as f:
        f.create_dataset(
            output_dataset_name,
            shape=(processor.size,),
            dtype=dt,
            chunks=True,
            compression=hdf5plugin.LZ4(),
        )

    angle_dict = {}
    vec_dict = {}

    with Progress() as bar:
        task = bar.add_task("Structural Info", total=processor.count())
        with h5py.File(hdf5_out, "r+") as f:
            n = 0
            for structural_info in processor.execute(
                callback=get_padded_structural_info,
                limit=None,
                params={
                    "padded_length": max_atoms,
                    "SASA": SASA,
                    "charge": charge,
                    "angles": vec_db is not None or angle_db is not None,
                },
                parallelism=parallelism,
            ):
                try:
                    if structural_info[0] is None:
                        raise ValueError("Structural_info[0] is None")

                    (
                        pdb,
                        atom_names,
                        elements,
                        res_ids,
                        coords,
                        sasas,
                        charges,
                        res_ids_per_residue,
                        angles,
                        norm_vecs,
                    ) = (*structural_info,)
                    pdb = os.path.basename(pdb)

                    if angle_db is not None or vec_db is not None:
                        for res_id, curr_angles, curr_norm_vecs in zip(
                            res_ids_per_residue, angles, norm_vecs
                        ):
                            res_id = "_".join([id_.decode("utf-8") for id_ in res_id])
                            angle_dict[res_id] = curr_angles.tolist()
                            vec_dict[res_id] = curr_norm_vecs.tolist()

                    len_dt = len(dt_arr)
                    f[output_dataset_name][n] = (
                        pdb,
                        atom_names,
                        elements,
                        res_ids,
                        coords,
                        sasas,
                        charges,
                    )[0:len_dt]

                    n += 1
                except Exception as e:
                    logger.warning("Failed to write PDB with the following error:")
                    logger.exception(e)
                finally:
                    bar.update(
                        task,
                        advance=1,
                        description=f"Structural Info: {n}/{processor.count()}",
                    )

            logger.info(f"PDBs successfully processed: {n}")
            f[output_dataset_name].resize((n,))

    if angle_db is not None:
        angle_db = sqlitedict.SqliteDict(angle_db, autocommit=False)
        for k, v in angle_dict.items():
            angle_db[k] = v
        angle_db.commit()
        angle_db.close()
        logger.info(f"Saved chi angles to {angle_db}")

    if vec_db is not None:
        vec_db = sqlitedict.SqliteDict(vec_db, autocommit=False)
        for k, v in vec_dict.items():
            vec_db[k] = v
        vec_db.commit()
        vec_db.close()
        logger.info(f"Saved normal vectors to {vec_db}")


def get_padded_structural_info(
    pdb_file: str,
    padded_length: int = 200000,
    SASA: bool = True,
    charge: bool = True,
    angles: bool = True,
) -> Tuple[
    bytes, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
]:
    """
    Extract structural info used for holographic projection from Biopython pose.

    Parameters
    ----------
    pdb_file: path to file with pdb
    padded_length: size to pad to
    SASA: Whether or not to calculate SASA
    charge: Whether or not to calculate charge
    angles: Whether or not to calculate anglges

    Returns
    -------
    tuple of (bytes, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray,
              np.ndarray)
        The entries in the tuple are
            bytes encoding the pdb name string
            bytes array encoding the atom names of shape [max_atoms]
            bytes array encoding the elements of shape [max_atoms]
            bytes array encoding the residue ids of shape [max_atoms,6]
            float array of shape [max_atoms,3] representing the 3D Cartesian
              coordinates of each atom
            float array of shape [max_atoms] storing the SASA of each atom
            float array of shape [max_atoms] storing the partial charge of each atom
    """

    try:
        pdb, ragged_structural_info = get_structural_info_from_protein(
            pdb_file,
            calculate_SASA=SASA,
            calculate_charge=charge,
            calculate_angles=angles,
        )

        mat_structural_info = pad_structural_info(
            ragged_structural_info, padded_length=padded_length
        )
    except Exception as e:
        logger.error(f"Failed to process {pdb_file}")
        logger.error(e)
        return (None,)

    return (pdb, *mat_structural_info)


def main():
    start_time = time.time()

    args = parse_args()
    logger.setLevel(args.logging)

    if args.pdb_dir is not None:
        if args.pdb_list_file is not None:
            with open(args.pdb_list_file, "r") as f:
                pdb_list = [pdb.strip() for pdb in f.readlines()]
        else:
            logger.info(
                "Generating a list of PDBs automatically from --pdb_dir. If this is not intended, use --pdb_list_file"
            )
            pdb_list = pdb_list_from_dir(args.pdb_dir)
    else:
        pdb_list = pdb_list_from_foldcomp(args.foldcomp)

    get_structural_info_from_dataset(
        args.input_path,
        pdb_list,
        args.max_atoms,
        args.hdf5_out,
        args.output_dataset_name,
        args.parallelism,
        args.angle_db,
        args.vec_db,
        args.SASA,
        args.charge,
    )

    logger.info(f"Total time = {time.time() - start_time:.2f} seconds")
