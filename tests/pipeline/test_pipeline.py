

import os, sys
import numpy as np
import h5py
import hdf5plugin

from copy import deepcopy

from zernikegrams import get_zernikegrams_from_pdbfile


get_structural_info_kwargs__template = {'padded_length': None,
                                'parser': 'biopython',
                                'SASA': True,
                                'charge': True,
                                'DSSP': False,
                                'angles': False,
                                'fix': True,
                                'hydrogens': True,
                                'extra_molecules': True,
                                'multi_struct': 'warn'}

get_neighborhoods_kwargs__template = {'r_max': 10.0,
                            'remove_central_residue': False,
                            'remove_central_sidechain': True,
                            'backbone_only': False,
                            'get_residues': None}

get_zernikegrams_kwargs__template = {'r_max': 10.0,
                            'radial_func_mode': 'ks',
                            'radial_func_max': 10,
                            'Lmax': 5,
                            'channels': ['C', 'N', 'O', 'S', 'H', 'SASA', 'charge'],
                            'backbone_only': False,
                            'request_frame': False,
                            'get_physicochemical_info_for_hydrogens': True,
                            'rst_normalization': 'square'}

def test_get_zernikegrams_from_pdbfile():

    '''
    Interestingly, values sometimes slightly differ, though I don't think enough to cause problems (10^-3 or 10^-4).
    I don't know what this is due to.
    The amount and location of differences is different between biopython and pyrosetta parsing.
    In both cases there seem to be regularities in which indices differ.
    '''

    os.system(f'structural-info \
                    --hdf5_out sinfo.hdf5 \
                    --pdb_dir ../data/pdbs \
                    --parser biopython \
                    --SASA \
                    --charge \
                    -F \
                    -H ')
    
    os.system(f'neighborhoods \
                    --hdf5_in  sinfo.hdf5 \
                    --hdf5_out nbs.hdf5 \
                    --remove_central_sidechain \
                    --r_max 10.0')
    
    os.system(f'zernikegrams \
                    --hdf5_in nbs.hdf5 \
                    --hdf5_out zgrams.hdf5 \
                    --rst_normalization square \
                    --radial_func_max 10 \
                    --l_max 5 \
                    --radial_func_mode ks \
                    --channels C,N,O,S,H,SASA,charge')
    
    pdbid = b'2fe3'

    with h5py.File('zgrams.hdf5', 'r') as f:
        res_ids_from_scripts = f['data']['res_id'][f['data']['res_id'][:, 1] == pdbid]
        zgrams_from_scripts = f['data']['zernikegram'][f['data']['res_id'][:, 1] == pdbid]


    data_from_pipeline = get_zernikegrams_from_pdbfile(f"../data/pdbs/{pdbid.decode('utf-8')}.pdb",
                                                        get_structural_info_kwargs__template,
                                                        get_neighborhoods_kwargs__template,
                                                        get_zernikegrams_kwargs__template)
    
    res_ids_from_pipeline = data_from_pipeline['res_id']
    zgrams_from_pipeline = data_from_pipeline['zernikegram']

    print(np.all(res_ids_from_scripts == res_ids_from_pipeline))


    for idx in range(res_ids_from_scripts.shape[0]):
        print()
        print(idx)
        print(np.all(res_ids_from_scripts[idx] == res_ids_from_pipeline[idx]))
        is_close = np.isclose(zgrams_from_scripts[idx], zgrams_from_pipeline[idx])
        print(is_close.all())
        print(np.sum(~is_close))
        if not is_close.all():
            print(zgrams_from_scripts[idx][~is_close])
            print(zgrams_from_pipeline[idx][~is_close])
            print(np.arange(len(is_close))[~is_close])
        print()



    os.remove('sinfo.hdf5')
    os.remove('nbs.hdf5')
    os.remove('zgrams.hdf5')






if __name__ == '__main__':
    test_get_zernikegrams_from_pdbfile()



