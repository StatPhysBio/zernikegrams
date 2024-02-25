import tempfile
import subprocess
import h5py
import hdf5plugin
import numpy as np
import pytest
import os


MISMATCH_TOL = 0.15  # Tolerance for discrepancies between reference pyrosetta structural infos and new biopython ones


reference_path = "tests/data/baseline_struct_info._hdf5"


@pytest.mark.order("first")
def test_make_tmpfile():
    global test_dir
    global test_path
    test_dir = tempfile.TemporaryDirectory()

    subprocess.run(
        f"structural-info --pdb_dir tests/data/pdbs -o {test_dir.name}/test.hdf5 --S -c --DSSP -H".split()
    )

    test_path = f"{test_dir.name}/test.hdf5"
    assert os.path.exists(test_path)


@pytest.mark.order("last")
def test_cleanup():
    test_dir.cleanup()


def test_secondary_structure_helix_matches_pyrosetta():
    reference_ss = {}
    with h5py.File(reference_path) as ref:
        res_ids = ref["data"]["res_ids"]
        for protein in res_ids:
            for item in protein:
                pdb = (
                    b"1hmd" if item[1] == b"1hm" else item[1]
                )  # annoying bug in reference implementation with .strip("pdb")
                reference_ss[(pdb, item[2], item[3])] = item[-1]

    test_ss = {}
    with h5py.File(test_path) as test:
        res_ids = test["data"]["res_ids"]
        for protein in res_ids:
            for item in protein:
                test_ss[(item[1], item[2], item[3])] = item[-1]

    mismatches = 0
    total = 0
    for key, val in reference_ss.items():
        if val == b"H":
            total += 1
            if test_ss[key] != b"H":
                mismatches += 1

    assert mismatches < total * MISMATCH_TOL


def test_number_of_atoms_matches_pyrosetta():
    with h5py.File(reference_path) as ref:
        ref_atoms = (
            (ref["data"]["elements"] != b"H") & (ref["data"]["elements"] != b"")
        ).sum()
        ref_H = (ref["data"]["elements"] == b"H").sum()

    with h5py.File(test_path) as test:
        test_atoms = (
            (test["data"]["elements"] != b"H") & (test["data"]["elements"] != b"")
        ).sum()
        test_H = (test["data"]["elements"] == b"H").sum()

    assert np.allclose([ref_atoms, ref_H], [test_atoms, test_H], rtol=MISMATCH_TOL)
