import setuptools
from setuptools.command.install import install
import os
import subprocess
import shutil


class CustomInstall(install):
    def run(self):
        install.run(self)
        
        self.install_reduce()
        self.install_openmm()
        self.install_pdb_fixer()
        

    def install_reduce(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reduce_path = os.path.join(dir_path, "zernikegrams/structural_info/reduce")
        dep_reduce_path = os.path.join(dir_path, "dependencies/reduce/reduce.zip")
        shutil.copyfile(dep_reduce_path, os.path.join(reduce_path, "reduce.zip"))
        
        os.chdir(reduce_path)
        subprocess.run(["unzip", "reduce.zip"])
        os.chdir(os.path.join(reduce_path, "reduce"))
        subprocess.run(["make"])

        os.chdir(dir_path)
        


    def install_openmm(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        openmm_path = os.path.join(dir_path, "dependencies/openmm")
        os.makedirs(openmm_path, exist_ok=True)
        os.chdir(openmm_path)
        subprocess.run(["unzip", "openmm.zip"])
        os.chdir(os.path.join(openmm_path, "openmm"))

        subprocess.run(["devtools/packaging/install.sh"])

        os.chdir(dir_path)

    
    def install_pdb_fixer(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        pdbfixer_path = os.path.join(dir_path, "dependencies/pdbfixer")
        os.makedirs(pdbfixer_path, exist_ok=True)
        os.chdir(pdbfixer_path)
        subprocess.run(["unzip", "pdbfixer.zip"])
        os.chdir(os.path.join(pdbfixer_path, "pdbfixer"))

        subprocess.run(["python", "setup.py", "install"])

        os.chdir(dir_path)



setuptools.setup(
    name="zernikegrams",
    version="0.1.0",
    description="Preprocessing routines for SO(3) equivariant protein structure tasks",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "structural-info = zernikegrams.structural_info.get_structural_info:main",
            "neighborhoods = zernikegrams.neighborhoods.get_neighborhoods:main",
            "zernikegrams = zernikegrams.holograms.get_holograms:main",
            "noise-neighborhoods = zernikegrams.add_noise.get_noised_nh:main"
        ]
    },
    include_package_data=True,
    cmdclass={"install": CustomInstall},
    install_requires=[
        "argparse",
        "biopython",
        "cmake",
        "foldcomp",
        "h5py",
        "hdf5plugin",
        "numpy<2", # pinned for openmm
        "pyopencl",
        "pytest",
        "torch",
        "rich",
        "scikit-learn",
        "sqlitedict",
        "stopit",
        "pyyaml",
    ]
)
