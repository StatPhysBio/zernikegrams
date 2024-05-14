import setuptools
from setuptools.command.install import install
import os
import subprocess


class CustomInstall(install):
    def run(self):
        install.run(self)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        reduce_path = os.path.join(dir_path, "zernikegrams/structural_info/reduce")
        os.makedirs(
            reduce_path,
            exist_ok=True
        )
        os.chdir(reduce_path)
        subprocess.run(
            ["git", "clone", "https://github.com/rlabduke/reduce.git"]
        )
        os.chdir(os.path.join(reduce_path, "reduce"))
        subprocess.run(["make"])

        # reduce's tests break our tests
        with open(os.path.join(reduce_path, "reduce/test/test_reduce.py"), "w") as w:
            w.write("\n")

        os.chdir(dir_path)
        

setuptools.setup(
    name="zernikegrams",
    version="0.1.0",
    description="Preprocessing routines for SO(3) equivariant protein structure tasks",
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    python_requires=">=3.9",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "structural-info = zernikegrams.structural_info.get_structural_info:main",
            "neighborhoods = zernikegrams.neighborhoods.get_neighborhoods:main",
            "zernikegrams = zernikegrams.holograms.get_holograms:main"
        ]
    },
    include_package_data=True,
    cmdclass={"install": CustomInstall}
)

