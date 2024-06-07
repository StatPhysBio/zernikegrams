
import os, sys



def test_keep_extra_mols():

    ## this fails if there are duplicate hydrogens

    os.makedirs('fixed_pdbs', exist_ok=True)

    os.system(f'structural-info \
                --hdf5_out sinfo.hdf5 \
                --pdb_dir tests/data/pdbs_with_hydrogens \
                --parser biopython \
                --SASA \
                --charge \
                -F \
                -H \
                --fixed_pdb_dir ./fixed_pdbs')
    
    os.system(f'structural-info \
                --hdf5_out sinfo.hdf5 \
                --pdb_dir tests/data/pdbs \
                --parser biopython \
                --SASA \
                --charge \
                -F \
                -H \
                --fixed_pdb_dir ./fixed_pdbs')
    
    os.system('rm sinfo.hdf5')

    # os.system('rm -r fixed_pdbs')


if __name__ == '__main__':
    test_keep_extra_mols()
