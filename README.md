# Zernikegrams

TODO (structural info):
 - Support MMFT files 
 - Write so many tests

TODO (general)
- finish structural info
- neighborhoods pipeline
- zernikegrams pipeline
- Data loaders from zernikegrams
- data loaders from pdbs/compressed pdbs (i.e., on the fly)
- Frame averaging + cartesian 3DDFT
- Support for other radial basis functions (e.g., bessel)?
- publish on pypi/conda/somewhere its easy to download from

## Installation
1. Clone this repo
2. run `conda env create -f env.yml`
3. `conda activate zernikegrams`
4. `pip install -e .`

## Usage
```
$ structural-info [options]
```
For example ,
```
$ structural-info --hdf5_out foo.hdf5 --pdb_dir tests/data/pdbs
```