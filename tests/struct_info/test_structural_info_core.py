import os

from src.structural_info.structural_info_core import  *

def test_get_structural_info_from_protein_basic():
    for file in os.listdir("tests/data/pdbs"):
        if not file.endswith("pdb"):
            continue
        get_structural_info_from_protein(f"tests/data/pdbs/{file}")