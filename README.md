# Zernikegrams

## Installation
Install with pip: 
```
pip install zernikegrams
```

### Dependencies
To successfully install with `pip install zernikegrams`, you must be able to install `pyopencl` and `h5py` with pip. Most machines can do this with no extra configuration. If yours is not one of them, install `ocl-icd-opencl-dev` and `libhdf5-dev` through your system's package manager.

This package currently depends on packages which can only be installed with `conda` or built from source, so a conda environment is recommended. 
1. Clone this repo and `cd zernikegrams/`
2.  
  - To create a new conda environment with necessary dependencies and this package installed: 
```
conda env create -f env.yml
conda activate zernikegrams
```
  - To install into an existing conda environment:
```
conda env update --name <existing env name> -f env.yml
```
  - To install without conda (coming soon: pip install support):
    - see env.yml for a list of required packages
    - From the root directory, run `pip install .`

## Usage
### CLI
When correctly installed, there are several CLI commands available:
1. `structural-info`: Processes .pdb files into parallel arrays of structural information, including [atom_name, element, SASA, charge, ...].
2. `neighborhoods`: Organize structual information into local neighborhoods centered at the alpha carbon of each residue.
3. `noise-neighborhoods`: Adds noise to the coordinates of the atoms in each neighborhood. Optional but useful for ensemble learning.
4. `zernikegrams`: Performs a spherical Fourier transform with the Zernike polynomials as a basis for each neighborhood. 
Each CLI command has many options, discoverable with `--help`.

Example:
```bash
$ structural-info --hdf5_out foo.hdf5 --pdb_dir tests/data/pdbs [--fix_pdbs --add_hydrogens --SASA --charge --DSSP ...]
$ neighborhoods  --hdf5_in foo.hdf5 --hdf5_out bar.hdf5 [--remove_central_residue --r_max 10 ...]
$ zernikegrams --hdf5_in bar.hdf5 --hdf5_out baz.hdf5  [--l_max 6 --r-max 10 ...]
```

## Python API
To access the package programmatically, import from `zernikegrams`. For example
```python
from zernikegrams.structural_info.RaSP import clean_pdb
from zernikegrams.holograms.get_holograms import get_single_zernikegram
```

## Development
### Testing
Tests should be run with `pytest` from the root directory.

### Roadmap
- Support MMFT files as well as .pdb files. Currently there is support for `foldcomp`, but not MMFT.
- Support for other radial basis functions (e.g., bessel)
- Dataloaders
  - From zernikegram .hdf5 files
  - On the fly: pdb files --> zernikegrams
  - Make pip installable
    - Need to build conda-only dependencies from source
    - Publish on pypi
