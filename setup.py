#!/usr/bin/env python

from setuptools import setup, find_packages
import glob

requirements = [line.rstrip() for line in open("requirements.txt", "rt")]

setup(
    name="eirepeat",
    version="1.0.1",
    description="eirepeat - EI Repeat Identification pipeline",
    author="Gemy Kaithakottil",
    author_email="Gemy.Kaithakottil@earlham.ac.uk",
    url="https://github.com/EI-CoreBioinformatics/eirepeat",
    license="GPLv3",
    zip_safe=False,
    keywords="repeat repeats transposon transposons helicase",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific Engineering :: Bio/Informatics",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": ["eirepeat = eirepeat.__main__:main"]},
    install_requires=requirements,
    packages=find_packages(".", exclude=["tests"]),
    scripts=[script for script in glob.glob("eirepeat/scripts/*")],
    package_data={
        "eirepeat.workflow": ["Snakefile"],
        "eirepeat.etc": [
            "hpc_config.json",
            "run_config.yaml",
            "eirepeat_config.yaml",
            "queryRepeatDatabase.tree.txt",
        ],
    },
    include_package_data=True,
)
