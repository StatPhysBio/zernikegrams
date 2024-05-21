

import os
import h5py
import hdf5plugin


if __name__ == '__main__':

    # os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')

    # os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs.hdf5 --remove_central_residue')


    with h5py.File('nbs.hdf5', "r") as f:
        num_nbs = len(f['data'])

        nb = f['data'][0]
    
    res_id = nb['res_id']
    res_ids = [r for r in res_id]





