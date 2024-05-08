import setuptools

setuptools.setup(
    name="zernikegrams",
    version="0.1.0",
    description="Preprocessing routines for SO(3) equivariant protein structure tasks",
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    python_requires=">=3.9",
    packages=setuptools.find_packages(),
    package_dir={
        "structural_info": "src",
    },
    entry_points={
        "console_scripts": [
            "structural-info = src.structural_info.get_structural_info:main",
            "neighborhoods = src.neighborhoods.get_neighborhoods:main",
            "zernikegrams = src.zernikegrams.get_zernikegrams:main"
        ]
    },
    include_package_data=True,
)