
import os
import h5py
import hdf5plugin
import numpy as np

reference_path = "tests/data/baseline_struct_info._hdf5"

def test_pyrosetta_flag():

    try:
        import pyrosetta
    except ModuleNotFoundError:
        print("[warning] Cannot import pyrosetta -- skipping pyrosetta test")
        return 

    os.system('structural-info --hdf5_out sinfo_pyrosetta_default.hdf5 --pdb_dir tests/data/pdbs --parser pyrosetta -F -H -S -c --DSSP')
    
    ref_pdb = b'2fe3'

    with h5py.File(reference_path) as ref:
        for i in range(len(ref['data'])):
            if ref['data'][i]['pdb'] == ref_pdb:
                true_mask = ref['data'][i]['atom_names'] != b''
                ref_num_atoms = np.sum(true_mask)
                ref_res_ids = ref['data'][i]['res_ids'][true_mask]
                ref_elements = ref['data'][i]['elements'][true_mask]
                ref_atom_names = ref['data'][i]['atom_names'][true_mask]
                ref_coords = ref['data'][i]['coords'][true_mask]
                ref_sasas = ref['data'][i]['SASAs'][true_mask]
                ref_charges = ref['data'][i]['charges'][true_mask]

    with h5py.File('sinfo_pyrosetta_default.hdf5') as test:
        for i in range(len(test['data'])):
            if test['data'][i]['pdb'] == ref_pdb:
                true_mask = test['data'][i]['atom_names'] != b''
                test_num_atoms = np.sum(true_mask)
                test_res_ids = test['data'][i]['res_ids'][true_mask]
                test_elements = test['data'][i]['elements'][true_mask]
                test_atom_names = test['data'][i]['atom_names'][true_mask]
                test_coords = test['data'][i]['coords'][true_mask]
                test_sasas = test['data'][i]['SASAs'][true_mask]
                test_charges = test['data'][i]['charges'][true_mask]

    assert ref_num_atoms == test_num_atoms
    assert np.all(ref_res_ids == test_res_ids)
    assert np.all(ref_elements == test_elements)
    assert np.all(ref_atom_names == test_atom_names)

    print('All tests passed!')

    os.remove('sinfo_pyrosetta_default.hdf5')
    

if __name__ == '__main__':
    test_pyrosetta_flag()
        
                



