from Bio.PDB import PDBParser
from zernikegrams.structural_info.RaSP import clean_pdb
import tempfile

def count_element_atoms(pdb_file, element="H"):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('structure', pdb_file)
    
    count = 0
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.element == element:
                        count += 1
                        
    return count

def test_no_hydrogens_respected():
    with tempfile.NamedTemporaryFile() as tmp:
        clean_pdb(
            "tests/data/pdbs/1MBO.pdb",
            tmp.name,
            "zernikegrams/structural_info/reduce/reduce/reduce_src/reduce",
            hydrogens=False,
            extra_molecules=False
        )

        assert count_element_atoms(tmp.name, "H") == 0


def test_yes_hydorgens_adds_H():
    with tempfile.NamedTemporaryFile() as tmp:
        clean_pdb(
            "tests/data/pdbs/1MBO.pdb",
            tmp.name,
            "zernikegrams/structural_info/reduce/reduce/reduce_src/reduce",
            hydrogens=True,
            extra_molecules=False
        )

        assert count_element_atoms(tmp.name, "H") > 0


def test_no_extra_molecules_removes_FE():
    with tempfile.NamedTemporaryFile() as tmp:
        clean_pdb(
            "tests/data/pdbs/1MBO.pdb",
            tmp.name,
            "zernikegrams/structural_info/reduce/reduce/reduce_src/reduce",
            hydrogens=False,
            extra_molecules=False
        )

        assert count_element_atoms(tmp.name, "FE") == 0


def test_yes_extra_molecules_keeps_FE():
    with tempfile.NamedTemporaryFile() as tmp:
        clean_pdb(
            "tests/data/pdbs/1MBO.pdb",
            tmp.name,
            "zernikegrams/structural_info/reduce/reduce/reduce_src/reduce",
            hydrogens=False,
            extra_molecules=True
        )

        assert count_element_atoms(tmp.name, "FE") == 1 
            