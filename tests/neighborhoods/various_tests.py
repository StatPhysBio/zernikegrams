

import os
import numpy as np
import h5py
import hdf5plugin

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def has_all_backbone_atoms_without_CA(atom_names):
    str_atom_names = [name.decode('utf-8').strip() for name in atom_names]
    return np.all(np.isin(['C', 'N', 'O'], str_atom_names))

def has_only_and_all_backbone_atoms_without_CA(atom_names):
    str_atom_names = [name.decode('utf-8').strip() for name in atom_names]
    return np.all(np.isin(str_atom_names, ['C', 'N', 'O'])) and np.all(np.isin(['C', 'N', 'O'], str_atom_names))

def has_all_backbone_atoms(atom_names):
    str_atom_names = [name.decode('utf-8').strip() for name in atom_names]
    return np.any(np.isin(['CA', 'C', 'N', 'O'], str_atom_names))

def has_only_and_all_backbone_atoms(atom_names):
    str_atom_names = [name.decode('utf-8').strip() for name in atom_names]
    return np.all(np.isin(str_atom_names, ['CA', 'C', 'N', 'O'])) and np.all(np.isin(['CA', 'C', 'N', 'O'], str_atom_names))


def test_keep_central_CA():

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs.hdf5 --coordinate_system cartesian --keep_central_CA')

    with h5py.File('nbs.hdf5', "r") as f:
        test_nbs = f['data'][:]
    
    has_CA = []
    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]

        str_central_atom_names = [name.decode('utf-8').strip() for name in central_atom_names]
        if 'CA' in str_central_atom_names:
            has_CA.append(True)
        else:
            has_CA.append(False)
        
        central_coords = nb['coords'][central_mask]
        central_CA_coords = central_coords[str_central_atom_names.index('CA')]
        assert np.allclose(central_CA_coords, np.array([0, 0, 0]))
    
    print(f'\n{np.sum(has_CA)}/{len(has_CA)} have CAs and should')

    os.remove('sinfo.hdf5')
    os.remove('nbs.hdf5')

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs.hdf5')

    with h5py.File('nbs.hdf5', "r") as f:
        test_nbs = f['data'][:]
    
    has_CA = []
    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]

        str_central_atom_names = [name.decode('utf-8').strip() for name in central_atom_names]
        if 'CA' in str_central_atom_names:
            has_CA.append(True)
        else:
            has_CA.append(False)
    
    print(f'\n{np.sum(has_CA)}/{len(has_CA)} have CAs and should NOT.')

    os.remove('sinfo.hdf5')
    os.remove('nbs.hdf5')



def test_remove_central_sidechain_and_not_backbone():

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs.hdf5 --remove_central_sidechain --keep_central_CA')

    with h5py.File('nbs.hdf5', "r") as f:
        test_nbs = f['data'][:]
    
    central_backbone_only = []
    central_backbone_only_without_CA = []

    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]

        central_backbone_only_without_CA.append(has_only_and_all_backbone_atoms_without_CA(central_atom_names))
        central_backbone_only.append(has_only_and_all_backbone_atoms(central_atom_names))

    print(f'\n{np.sum(central_backbone_only)}/{len(central_backbone_only)} have only backbone atoms and should')
    print(f'\n{np.sum(central_backbone_only_without_CA)}/{len(central_backbone_only_without_CA)} have only backbone atoms without CA and should NOT')
    
    os.remove('sinfo.hdf5')
    os.remove('nbs.hdf5')
    

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs.hdf5 --remove_central_sidechain')

    with h5py.File('nbs.hdf5', "r") as f:
        test_nbs = f['data'][:]
    
    central_backbone_only = []
    central_backbone_only_without_CA = []

    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]

        central_backbone_only_without_CA.append(has_only_and_all_backbone_atoms_without_CA(central_atom_names))
        central_backbone_only.append(has_only_and_all_backbone_atoms(central_atom_names))

    print(f'\n{np.sum(central_backbone_only)}/{len(central_backbone_only)} have only backbone atoms and should NOT')
    print(f'\n{np.sum(central_backbone_only_without_CA)}/{len(central_backbone_only_without_CA)} have only backbone atoms without CA and should')
    
    os.remove('sinfo.hdf5')
    os.remove('nbs.hdf5')


def test_align_with_backbone_frame():

    os.system('structural-info --hdf5_out sinfo.hdf5 --pdb_dir ../data/pdbs')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs_aligned.hdf5 --coordinate_system cartesian --remove_central_sidechain --align_to_backbone_frame')
    os.system('neighborhoods --hdf5_in sinfo.hdf5 --hdf5_out nbs_not_aligned.hdf5 --coordinate_system cartesian --remove_central_sidechain')

    with h5py.File('nbs_aligned.hdf5', "r") as f:
        test_nbs = f['data'][:40]
    N_coords = []
    C_coords = []
    O_coords = []
    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]
        central_coords = nb['coords'][central_mask]
        N_coords.append(central_coords[np.where(central_atom_names == b'N   ')[0][0]])
        C_coords.append(central_coords[np.where(central_atom_names == b'C   ')[0][0]])
        O_coords.append(central_coords[np.where(central_atom_names == b'O   ')[0][0]])
    N_coords = np.vstack(N_coords)
    C_coords = np.vstack(C_coords)
    O_coords = np.vstack(O_coords)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(N_coords[:, 0], N_coords[:, 1], N_coords[:, 2], c='blue', marker='o', label='N')
    ax.scatter(C_coords[:, 0], C_coords[:, 1], C_coords[:, 2], c='red', marker='o', label='C')
    ax.scatter(O_coords[:, 0], O_coords[:, 1], O_coords[:, 2], c='green', marker='o', label='O')
    ax.scatter([0], [0], [0], c='black', marker='x', label='Central CA')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.savefig('plot_aligned_to_frame.png')
    plt.close()

    with h5py.File('nbs_not_aligned.hdf5', "r") as f:
        test_nbs = f['data'][:40]
    N_coords = []
    C_coords = []
    O_coords = []
    for nb in test_nbs:
        res_id = nb['res_id']
        res_ids = nb['res_ids']
        central_mask = np.logical_and.reduce(res_ids == res_id, axis=-1)
        central_res_ids = res_ids[central_mask]
        central_atom_names = nb['atom_names'][central_mask]
        central_coords = nb['coords'][central_mask]
        N_coords.append(central_coords[np.where(central_atom_names == b'N   ')[0][0]])
        C_coords.append(central_coords[np.where(central_atom_names == b'C   ')[0][0]])
        O_coords.append(central_coords[np.where(central_atom_names == b'O   ')[0][0]])
    N_coords = np.vstack(N_coords)
    C_coords = np.vstack(C_coords)
    O_coords = np.vstack(O_coords)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(N_coords[:, 0], N_coords[:, 1], N_coords[:, 2], c='blue', marker='o', label='N')
    ax.scatter(C_coords[:, 0], C_coords[:, 1], C_coords[:, 2], c='red', marker='o', label='C')
    ax.scatter(O_coords[:, 0], O_coords[:, 1], O_coords[:, 2], c='green', marker='o', label='O')
    ax.scatter([0], [0], [0], c='black', marker='x', label='Central CA')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.savefig('plot_not_aligned_to_frame.png')
    plt.close()
    
    os.remove('sinfo.hdf5')
    os.remove('nbs_aligned.hdf5')
    os.remove('nbs_not_aligned.hdf5')
    


if __name__ == '__main__':

    # print(has_only_backbone_atoms_without_CA([b'C  ', b'N  ', b'O  ']))
    # print(has_only_backbone_atoms_without_CA([b'C  ', b'N  ']))
    # print(has_only_backbone_atoms_without_CA([b'C  ', b'N  ', b'O  ', b'CB  ']))
    # print(has_all_backbone_atoms_without_CA([b'C  ', b'N  ', b'O  ', b'CB  ']))
    # print(has_all_backbone_atoms_without_CA([b'C  ', b'N  ', b'CB  ']))

    # test_keep_central_CA()

    # test_remove_central_sidechain_and_not_backbone()

    test_align_with_backbone_frame()



