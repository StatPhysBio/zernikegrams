import tempfile
import subprocess
import h5py
import hdf5plugin

import numpy as np


def test_struct_info_matches_old():
   """
   TODO: check that the structural info in baseline_struct_info._hdf5
   matches the structural info calculated with 
   `subprocess.run(f"structural-info --hdf5_out {td}/foo.hd5f --pdb_dir tests/data/pdbs".split())`

   How to do this? Biopython and pyrosetta disagree about some atoms
   """
   pass