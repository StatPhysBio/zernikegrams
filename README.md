# Zernikegrams

## Installation
```
conda install zernikegrams -c statphysbio -c conda-forge
```

### Requirements
Zernikegrams is distributed through the anaconda package manager, which provides most dependencies in most cases. Notable exceptions include:
- `foldcomp`, which is optional and only necessary if using `--foldcomp` with `structural-info`. If you are, you probably already have it installed, but you can install it with `pip install foldcomp` if not.
- `DSSP`, which is optional and only necessary if using `--DSSP` with `structural-info`. On Mac, this can be installed with `brew install brewsci/bio/dssp`; on Linux, use `conda install dssp -c salilab`.
- A modern GCC compiler. Most machines have one already, but if you see cryptic messages referencing "GLIBCXX_3.4.30 not found", try `conda install libstdcxx-ng -conda-forge` (if on Linux). 
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

4. Build Reduce, the program for adding hydrogens. The easiest way to do this is with
```
PREFIX=$HOME/local bash devtools/conda-build/pre-link.sh
```
Which installs the reduce executable in $HOME/local/bin, where structural_info_core expects it. $PREFIX can be something
other than $HOME/local, as long as it's not the current working directory. This will not change where reduce is installed, just where some
temporary files live.

5. Install zernikegrams
```
pip install -e . -vv
```
`-e` is for editable mode (changes take effect without reinstalling) and `-vv` is very verbose. Either can be changed.

6. Optionally, install DSSP. This is only necessary for calculating secondary structure, but is needed for some tests. Use `conda install dssp -c salilab` or `brew install brewsci/bio/dssp` depending on your OS.
  
7. Run `pytest` from the root directory--if everything passes, you're good to go!

### Testing
Tests should be run with `pytest` from the root directory. It is polite to include new tests with new code (if it can be reasonably tested) and to ensure that new code doesn't break old tests. Bug fixes should include at least one test that fails without the fix and passes with it.

### Releases
If you would like your changes to be reflected in the latest version of the package that's pulled from conda, create a new release. In GitHub, find the "Releases" section (on the right) and follow the instructions. It's polite to version your release as [MAJOR.MINOR.PATCH](https://semver.org/) and provide a detailed description of updates. When you create a new version, a GitHub Actions script will run and (if successful) automatically update the Anaconda repository.

### GitHub Actions
On every push to every branch, `.github/workflows/run-tests.yml` builds the repo from scratch using conda, configures the environment, installs DSSP, and runs `pytest`. If it passes, a green check mark shows up. Currently, we only test using python 3.9 on a Linux x86-64 machine. In the future, we might want to test on more Python versions and macos-13 (x86) and macos-latest (arm)--probably only on pushes to main--using `matrix`. 

On every release, `.github/workflows/build_and_upload_conda.yaml` runs, which updates the Anaconda repository. It was configured using [this tutorial](https://github.com/marketplace/actions/build-and-upload-conda-packages). In `devtools/` there is the `meta.yaml` file that conda uses to build the package.

### Building Dependencies from Source
Most Anaconda packages distribute compiled binaries, not source code. Due to limitations of GH Actions runners (e.g., no Linux arm support), it's problematic to rely on GH Actions to compile and distribute code that we need to build from source.

Currently, the only example of this is Reduce. Our approach is to put the build-from-source code in `devtools/conda-build/pre-link.sh`, which conda automatically runs on every local machine when zernikegrams is installed. 

Another great candidate for build-from-source would be DSSP (currently, users are responsible for getting it themselves), probably from the [PDB-REDO implementation](https://github.com/PDB-REDO/dssp). Note: I (William) have never been able to build this package from source--you'll know you're successful when you have a DSSP executable and can run `<executable> path-to-pdb-file` and the output looks reasonable. If you can do that, then in `structural_info_core`, find the call to `dssp_dict_from_pdb_file` and pass `DSSP=<executable-path>` as a key-word argument. 

In general: all of the binaries we compile should be installed in the same, **non-root**, location. Currently, `$HOME/local` seems reasonable. If the code we're compiling uses `cmake`, then `-DCMAKE_INSTALL_PREFIX=$HOME/local` should do that. 

### Roadmap
- Support MMFT files as well as .pdb files. Currently there is support for `foldcomp`, but not MMFT.
- Support for other radial basis functions (e.g., bessel)
- Dataloaders
  - From zernikegram .hdf5 files
  - On the fly: pdb files --> zernikegrams
