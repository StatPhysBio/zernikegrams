# Zernikegrams

## Installation
```
conda install zernikegrams -c statphysbio -c conda-forge -c bioconda
```
This installs zernikegrams (our package) and its dependencies in an existing conda environment. 
Common issues:
- *dssp requires libzlib >=1.3.1 but everything else requires libzlib <1.3* Fix: make sure to install with -c statphysbio before -c bioconda. statphysbio specifically builds a version of dssp for this reason! (But bio conda is still necessary for `reduce`)
  
### Requirements
Zernikegrams is distributed through the anaconda package manager, which provides most dependencies in most cases. Notable exceptions include:
- `foldcomp`, which is optional and only necessary if using `--foldcomp` with `structural-info`. If you are, you probably already have it installed, but you can install it with `pip install foldcomp` if not.
- `argparse`, which comes with almost all Python distributions, but (apparently) not all and is (apparently) not installable with conda. Try `pip install argparse`. 

### Supported Platforms
This package should work on any permutation of {mac, linux} X {x86-64, arm64}. Though the package itself is OS-agnostic, its dependencies (namely OpenMM) are not. 

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
### Building locally
1. Clone this repo
2. If necessary, install conda-build with `conda install conda-build`
3. Install the dependencies for this repo with 
```
conda build devtools/conda-build --no-test --output-folder ./build -c conda-forge
conda install zernikegrams -c ./build -c conda-forge --only-deps
```
This installs the dependencies, but not zernikegrams itself. If the dependencies haven't changed since
the latest release, you can also use `conda  install zernikegrams -c statphysbio -c conda-forge --only-deps`
4. Install zernikegrams
```
pip install -e . -vv
```
`-e` is for editable mode (changes take effect without reinstalling) and `-vv` is very verbose. Either can be changed.
  
1. Run `pytest` from the root directory--if everything passes, you're good to go!

### Testing
Tests should be run with `pytest` from the root directory. It is polite to include new tests with new code (if it can be reasonably tested) and to ensure that new code doesn't break old tests. Bug fixes should include at least one test that fails without the fix and passes with it.

### Releases
If you would like your changes to be reflected in the latest version of the package that's pulled from conda, create a new release. In GitHub, find the "Releases" section (on the right) and follow the instructions. It's polite to version your release as [MAJOR.MINOR.PATCH](https://semver.org/) and provide a detailed description of updates. When you create a new version, a GitHub Actions script will run and (if successful) automatically update the Anaconda repository.

### GitHub Actions
On every push to every branch, `.github/workflows/run-tests.yml` builds the repo from scratch using conda, configures the environment, and runs `pytest`. If it passes, a green check mark shows up. Currently, we only test using python 3.9 on a Linux x86-64 machine. In the future, we might want to test on more Python versions and macos-13 (x86) and macos-latest (arm)--probably only on pushes to main--using `matrix`. 

On every release, `.github/workflows/build_and_upload_conda.yaml` runs, which updates the Anaconda repository. It was configured using [this tutorial](https://github.com/marketplace/actions/build-and-upload-conda-packages). In `devtools/` there is the `meta.yaml` file that conda uses to build the package.

### Dependencies
Dependencies come in two kinds: those that can be installed with conda and those that cannot. If the can't be installed with conda, they should be built from source (see below) or the user should be asked to install it themself. 

Dependencies that are available through conda are listed in `devtools/conda-build/meta.yaml` under "requirements" > "run". To add a new dependency, simply add it to that list. If it's not available through conda-forge or the "defaults" conda channel, update `devtools/conda-envs/build_env.yaml` with the new channel, so that the automated testing and build process can find it. 

These dependencies are automatically downloaded and installed when `conda install zernikegrams` is run. 

### `pip` Dependencies
Some packages are available through pip but not conda. Where possible, these should be avoided. Conda cannot install pip packages. One option is to ask users to install it themselves (e.g. we ask them to install foldcomp). Another is to use `grayskull` or a similar tool to convert a pip package to a conda package, and host it ourselves in the statphysbio Anaconda channel.

As a last resort, we could put `pip install ...` in `post-link.sh`. This is considered extremely bad practice. 

### Building Dependencies from Source
Most Anaconda packages distribute compiled binaries, not source code. Due to limitations of GH Actions runners (e.g., no Linux arm support), it's problematic to rely on GH Actions to compile and distribute code that we need to build from source.

### Roadmap
- Support MMFT files as well as .pdb files. Currently there is support for `foldcomp`, but not MMFT.
- Support for other radial basis functions (e.g., bessel)
- Dataloaders
  - From zernikegram .hdf5 files
  - On the fly: pdb files --> zernikegrams
