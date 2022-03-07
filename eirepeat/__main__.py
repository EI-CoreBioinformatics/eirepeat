#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

EI Repeat Identification Pipeline

"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__license__ = "GNU General Public License v3.0"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "Gemy.Kaithakottil@gmail.com"

# import libraries
import argparse
from argparse import RawTextHelpFormatter
import os
import sys
import subprocess
import yaml
import pkg_resources
from eirepeat.scripts.jiracomms import JiraInfo, post_to_jira
from eirepeat import (
    DEFAULT_PAP_CONFIG_FILE,
    DEFAULT_PAP_RUN_CONFIG_FILE,
    DEFAULT_HPC_CONFIG_FILE,
)

from snakemake.utils import min_version

min_version("7.0")

# get script name
script = os.path.basename(sys.argv[0])
script_dir = pkg_resources.resource_filename("eirepeat", "workflow")


class RepeatsPipeline:
    def __init__(self, args):
        print("Initialising pipeline")
        self.args = args
        self.jira = args.jira
        self.run_config = args.run_config
        self.hpc_config = args.hpc_config
        self.jobs = args.jobs
        self.latency_wait = args.latency_wait
        self.no_posting = args.no_posting
        self.verbose = args.verbose
        self.dry_run = args.dry_run
        self.loaded_run_config = yaml.load(
            open(self.run_config), Loader=yaml.SafeLoader
        )
        self.output = self.loaded_run_config["output"]
        self.species = self.loaded_run_config["species"]

        # Load the config file
        self.pap_config = yaml.load(
            open(DEFAULT_PAP_CONFIG_FILE), Loader=yaml.SafeLoader
        )

        # Gets JIRA ticket from server (or makes one from args provided if args are set appropriately)
        JiraInfo(self.jira).initialise(pap_config=self.pap_config)

    def run(self):
        print("Running the pipeline..")
        cmd = None
        if self.dry_run:
            print("Enabling dry run..")
            cmd = (
                f"snakemake --snakefile {script_dir}/Snakefile"
                f" --configfile {self.run_config} --latency-wait {self.latency_wait} --jobs {self.jobs} --cluster-config {self.hpc_config}"
                f" --config ppbfx={self.jira} notify={self.no_posting} verbose={self.verbose}"
                f" --drmaa ' -p {{cluster.partition}} -c {{cluster.cores}} --mem={{cluster.memory}} -J {{cluster.J}}' -np "
            )
            print(cmd)

        else:
            cmd = (
                f"mkdir -p logs && snakemake --snakefile {script_dir}/Snakefile"
                f" --configfile {self.run_config} --latency-wait {self.latency_wait} --jobs {self.jobs} --cluster-config {self.hpc_config}"
                f" --config ppbfx={self.jira} notify={self.no_posting} verbose={self.verbose}"
                f" --drmaa ' -p {{cluster.partition}} -c {{cluster.cores}} --mem={{cluster.memory}} -J {{cluster.J}} -o logs/{{rule}}.%N.%j.cluster.log' --printshellcmds --reason "
            )

        # for universal_newlines - https://stackoverflow.com/a/4417735
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )
        # https://www.programcreek.com/python/example/50/subprocess.Popen
        (result, error) = p.communicate()
        exit_code = p.returncode
        if exit_code:
            raise subprocess.CalledProcessError(exit_code, cmd)
        print(f"\nRESULTS:\n{result}\n\nERRORS:\n{error}\n")

        if self.dry_run:
            print("Dry run completed successfully!\n")
        else:
            print(
                f"EIREPEAT completed successfully!\n\n"
                f"The output directory is below:\n{self.output}\n\n"
                f"- *Repeatmodeler*:\n"
                f"- Repeatmodeler genome index directory:\n"
                f"{self.output}/index\n"
                f"- Repeatmodeler output files:\n"
                f"{self.output}/index/genome_db-families.(fa,stk)\n\n"
                f"- *RepeatMasker*:\n"
                f"- RepeatMasker output using RepeatModeler repeats (interspersed):\n"
                f"{self.output}/RepeatMasker_interspersed_repeatmodeler\n"
                f"- RepeatMasker output using RepeatMasker library '{self.species}' repeats (interspersed):\n"
                f"{self.output}/RepeatMasker_interspersed\n"
                f"- RepeatMasker output using RepeatMasker library '{self.species}' repeats (low-complexity):\n"
                f"{self.output}/RepeatMasker_low\n"
            )


def main():
    parser = argparse.ArgumentParser(
        description="EI Repeat Identification Pipeline",
        formatter_class=RawTextHelpFormatter,
        epilog="Example command:\n"
        + script
        + " PPBFX-611 --run_config [run_config.yaml]"
        + "\n\nContact:"
        + __author__
        + "("
        + __email__
        + ")",
    )
    parser.add_argument(
        "jira", help="Provide JIRA id for posting job summary. E.g., PPBFX-611"
    )
    parser.add_argument(
        "--run_config",
        required=True,
        help=f"Provide run configuration YAML (Use template: {DEFAULT_PAP_RUN_CONFIG_FILE})",
    )
    parser.add_argument(
        "--hpc_config",
        default=DEFAULT_HPC_CONFIG_FILE,
        help="Provide HPC configuration YAML (default: %(default)s)",
    )
    parser.add_argument(
        "--jobs",
        "-j",
        default=100,
        help="Use at most N CPU cluster/cloud jobs in parallel (default: %(default)s)",
    )
    parser.add_argument(
        "--latency_wait",
        default=120,
        help="Wait given seconds if an output file of a job is not present after the job finished (default: %(default)s)",
    )
    parser.add_argument(
        "--no_posting",
        action="store_true",
        help="Use this flag if you are testing and do not want to post comments to JIRA tickets (default: %(default)s)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode for debugging (default: %(default)s)",
    )
    parser.add_argument(
        "-np", "--dry_run", action="store_true", help="Dry run (default: %(default)s)"
    )

    args = parser.parse_args()

    RepeatsPipeline(args).run()


if __name__ == "__main__":
    main()
