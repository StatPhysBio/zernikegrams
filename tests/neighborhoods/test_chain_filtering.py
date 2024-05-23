

import os
import numpy as np
import h5py
import hdf5plugin


def test_chain_filtering_small_example():

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir tests/data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs_all_chains.hdf5 --remove_central_sidechain --keep_central_CA')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs_filtered_chains.hdf5 --pdb_chain_pairs_to_consider_filepath tests/data/pdbs/pdb_chain_pairs.txt --remove_central_sidechain --keep_central_CA')


    with h5py.File('nbs_all_chains.hdf5', "r") as f:
        nbs = f['data'][:]
        num_nbs = len(nbs)
        print(f'Number of neighborhoods WITHOUT filtering chains: {num_nbs}')

        pdb_chain_pairs = set()
        for nb in nbs:
            pdb_chain_pairs.add('_'.join([nb['res_id'][1].decode('utf-8'), nb['res_id'][2].decode('utf-8')]))
        print(f'pd_chain pairs WITHOUT filtering: {pdb_chain_pairs}')
        
    
    with h5py.File('nbs_filtered_chains.hdf5', "r") as f:
        nbs = f['data'][:]
        num_nbs = len(nbs)
        print(f'Number of neighborhoods WITH filtering chains: {num_nbs}')

        pdb_chain_pairs = set()
        for nb in nbs:
            pdb_chain_pairs.add('_'.join([nb['res_id'][1].decode('utf-8'), nb['res_id'][2].decode('utf-8')]))
        print(f'pd_chain pairs WITH filtering: {pdb_chain_pairs}')

    os.remove('sinfo.hdf5')
    os.remove('nbs_all_chains.hdf5')
    os.remove('nbs_filtered_chains.hdf5')

    


if __name__ == '__main__':

    test_chain_filtering_small_example()





