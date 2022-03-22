#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to create the run_config.yaml

"""

# authorship
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "gemygk@gmail.com"

# import libraries
import argparse
from pathlib import Path
import sys
import os
import yaml
from eirepeat import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_HPC_CONFIG_FILE,
    FULL_SPECIES_TREE_FILE,
)

# get script name
script = Path(sys.argv[0]).name

cwd = os.getcwd()


class EIRepeatConfigure:
    def __init__(self, args):
        self.args = args
        if not Path(self.args.fasta).exists():
            raise FileNotFoundError(f"File not found: '{self.args.fasta}'")
        self.args.fasta = str(Path(self.args.fasta).resolve())
        if self.args.close_reference:
            if not Path(self.args.close_reference).exists():
                raise FileNotFoundError(
                    f"File not found: '{self.args.close_reference}'"
                )
            self.args.close_reference = str(Path(self.args.close_reference).resolve())
        if self.args.organellar_fasta:
            if not Path(self.args.organellar_fasta).exists():
                raise FileNotFoundError(
                    f"File not found: '{self.args.organellar_fasta}'"
                )
            self.args.organellar_fasta = str(Path(self.args.organellar_fasta).resolve())
        self.args.output = str(Path(self.args.output).resolve())
        self.args.logs = str(Path(self.args.output).resolve() / "logs")
        self.run_config = dict()
        self.run_config_file = str()

    def process_run_config(self):
        with open(DEFAULT_CONFIG_FILE, "r") as fh:
            try:
                self.run_config = yaml.safe_load(fh)
            except yaml.YAMLError as err:
                print(err)
        if not self.run_config:
            raise ValueError(
                f"No information processed from run_config file - '{self.args.run_config}'"
            )

    def write_run_config(self):
        # output directory
        self.run_config["fasta"] = self.args.fasta
        self.run_config["species"] = self.args.species
        self.run_config["run_red_repeats"] = self.args.run_red_repeats
        self.run_config["close_reference"] = self.args.close_reference
        self.run_config["organellar_fasta"] = self.args.organellar_fasta
        self.run_config["output"] = self.args.output
        self.run_config["logs"] = self.args.logs

        Path(self.args.logs).mkdir(parents=True, exist_ok=True)
        # modify any additional defaults
        self.run_config["hpc_config"] = DEFAULT_HPC_CONFIG_FILE
        self.run_config["jira"]["jira_id"] = self.args.jira
        # write the new run config file
        with open(self.run_config_file, "w") as fh:
            yaml.dump(self.run_config, fh, sort_keys=False)

    def run(self):
        self.process_run_config()
        self.run_config_file = os.path.join(self.args.output, "run_config.yaml")
        self.write_run_config()
        print(f"\nGreat! Created run_config file: '{self.run_config_file}'\n")


def main():

    parser = argparse.ArgumentParser(description="Script to create the run_config.yaml")
    parser.add_argument("fasta", help="Provide fasta file")
    parser.add_argument(
        "--species",
        required=True,
        default=None,
        help=f"Provide species name. Please use the file here to identify the species. Also, check the NCBI taxonomy to identify the correct species option - https://www.ncbi.nlm.nih.gov/taxonomy: {FULL_SPECIES_TREE_FILE} (default: %(default)s)",
    )
    parser.add_argument(
        "--run_red_repeats",
        action="store_true",
        help="Enable this option to generate RED repeats, in addition (default: %(default)s)",
    )
    parser.add_argument(
        "--close_reference",
        help="Provide a close reference protein CDS fasta to mask the RepeatModeler fasta. Try to extract just protein coding models and remove any models identified as repeat associated from this file (default: %(default)s)",
    )
    parser.add_argument(
        "--organellar_fasta",
        help="Provide organellar chloroplast|mitrochondrial nucleotide fasta to mask the RepeatModeler fasta. Use provided script ncbi_download.py to download this fasta file from NCBI (default: %(default)s)",
    )
    parser.add_argument(
        "--jira",
        help="Provide JIRA id for posting job summary. E.g., PPBFX-611 (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=os.path.join(cwd, "output"),
        help="Provide output directory (default: %(default)s)",
    )
    args = parser.parse_args()
    EIRepeatConfigure(args).run()


if __name__ == "__main__":
    main()
