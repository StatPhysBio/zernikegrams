import setuptools

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
)

