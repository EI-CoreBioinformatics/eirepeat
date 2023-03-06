#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

EI Repeat Identification Pipeline

"""

# authorship
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "gemygk@gmail.com"

# import libraries
import argparse
import os
import sys
import subprocess
import yaml
import pkg_resources

from eirepeat import __version__
from eirepeat.scripts.jiracomms import JiraInfo
from eirepeat.scripts.eirepeat_configure import EIRepeatConfigure
from eirepeat import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_HPC_CONFIG_FILE,
    FULL_SPECIES_TREE_FILE,
)

from snakemake.utils import min_version

min_version("7.0")

# get script name
script = os.path.basename(sys.argv[0])
script_dir = pkg_resources.resource_filename("eirepeat", "workflow")
cwd = os.getcwd()


def command_configure(args):
    print("Running configure..")
    # check if we have a config file
    run_config = False
    run_config_file = os.path.join(args.output, "run_config.yaml")
    try:
        run_config = os.path.exists(run_config_file)
    except:
        pass
    if run_config is False or args.force_reconfiguration:
        EIRepeatConfigure(args).run()
    elif run_config:
        print(
            f"\nWARNING: Configuration file '{run_config_file}' already present. Please set --force-reconfiguration/-f to override this.\n"
        )


def command_run(args):
    EIRepeat(args).run()


class EIRepeat:
    def __init__(self, args):
        print("Initialising pipeline")
        self.args = args
        self.run_config = args.run_config
        self.hpc_config = args.hpc_config
        self.jobs = args.jobs
        self.latency_wait = args.latency_wait
        self.no_posting = args.no_posting
        self.verbose = args.verbose
        self.exclude_hosts = args.exclude_hosts
        self.dry_run = args.dry_run
        self.loaded_run_config = yaml.load(
            open(self.run_config), Loader=yaml.SafeLoader
        )
        self.jira_id = self.loaded_run_config["jira"]["jira_id"]
        self.output = self.loaded_run_config["output"]
        self.species = self.loaded_run_config["species"]
        self.run_red_repeats = self.loaded_run_config["run_red_repeats"]
        self.logs = self.loaded_run_config["logs"]
        # for summary
        self.index_name = self.loaded_run_config["prefix"]["index_name"]
        self.eirepeat_completed = os.path.join(
            self.loaded_run_config["output"], "eirepeat.completed.txt"
        )

        # Load the config file
        self.pap_config = yaml.load(open(DEFAULT_CONFIG_FILE), Loader=yaml.SafeLoader)

        # Gets JIRA ticket from server (or makes one from args provided if args are set appropriately)
        if self.jira_id:
            JiraInfo(self.jira_id).initialise(pap_config=self.pap_config)

    def run(self):
        print("Running the pipeline..")
        cmd = None
        if self.dry_run:
            print("Enabling dry run..")
            cmd = (
                f"snakemake --snakefile {script_dir}/Snakefile"
                f" --configfile {self.run_config} --latency-wait {self.latency_wait} --jobs {self.jobs} --cluster-config {self.hpc_config}"
                f" --config notify={self.no_posting} verbose={self.verbose} -np --reason"
            )
            cmd += (
                " --drmaa ' -p {cluster.partition} -c {cluster.cores} --mem={cluster.memory} -J {cluster.J} --exclude={cluster.exclude}'"
                if self.exclude_hosts
                else " --drmaa ' -p {cluster.partition} -c {cluster.cores} --mem={cluster.memory} -J {cluster.J}'"
            )
            print(cmd)

        else:
            cmd = (
                f"snakemake --snakefile {script_dir}/Snakefile"
                f" --configfile {self.run_config} --latency-wait {self.latency_wait} --jobs {self.jobs} --cluster-config {self.hpc_config}"
                f" --config notify={self.no_posting} verbose={self.verbose}"
                " --printshellcmds --reason "
            )
            cmd += (
                f" --drmaa ' -p {{cluster.partition}} -c {{cluster.cores}} --mem={{cluster.memory}} -J {{cluster.J}} -o {self.logs}/{{rule}}.%N.%j.cluster.log --exclude={{cluster.exclude}}'"
                if self.exclude_hosts
                else f" --drmaa ' -p {{cluster.partition}} -c {{cluster.cores}} --mem={{cluster.memory}} -J {{cluster.J}} -o {self.logs}/{{rule}}.%N.%j.cluster.log'"
            )

        # for universal_newlines - https://stackoverflow.com/a/4417735
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True
        )
        # https://www.programcreek.com/python/example/50/subprocess.Popen
        (result, error) = p.communicate()
        exit_code = p.returncode
        print(f"\nRESULTS:\n{result}\n\nERRORS:\n{error}\n\nEXIT_CODE:\n{exit_code}\n")
        if exit_code:
            raise subprocess.CalledProcessError(exit_code, cmd)

        if self.dry_run:
            print("Dry run completed successfully!\n")
        else:
            print(
                f"EIREPEAT completed successfully!\n\n"
                f"The output directory is below:\n{self.output}"
                # f"\n\nRepeatModeler\n"
                # f"RepeatModeler output files:\n"
                # f"{self.output}/index/{self.index_name}-families.fa\n"
                # f"{self.output}/index/{self.index_name}-families.stk"
                f"\n\nRepeatMasker\n"
                f"RepeatMasker output using RepeatMasker library '{self.species}' repeats (low-complexity):\n"
                f"{self.output}/RepeatMasker_low/{self.index_name}.out.gff\n"
                f"{self.output}/RepeatMasker_low/{self.index_name}.out.gff3\n"
                f"\nRepeatMasker output using RepeatMasker library '{self.species}' repeats (interspersed):\n"
                f"{self.output}/RepeatMasker_interspersed/{self.index_name}.out.gff\n"
                f"{self.output}/RepeatMasker_interspersed/{self.index_name}.out.gff3\n"
                f"\nRepeatMasker output using RepeatModeler repeats (interspersed):\n"
                f"{self.output}/RepeatMasker_interspersed_repeatmodeler/{self.index_name}.out.gff\n"
                f"{self.output}/RepeatMasker_interspersed_repeatmodeler/{self.index_name}.out.gff3\n"
                f"\n\nMain output files\n"
                f"All repeats (low + interspersed):\n"
                f"{self.output}/all_repeats.raw.out.gff\n"
                f"{self.output}/all_repeats.gff3\n"
                f"\nAll interspersed repeats (interspersed):\n"
                f"{self.output}/all_interspersed_repeats.raw.out.gff\n"
                f"{self.output}/all_interspersed_repeats.gff3\n"
            )
            if self.run_red_repeats:
                print(
                    f"\n\nAdditional repeats:\n"
                    f"RED Repeats\n"
                    f"{self.output}/red/genome.rpt.gff3\n\n"
                )
            # print stats
            with open(self.eirepeat_completed, "r") as fh:
                print_now = False
                for line in fh:
                    line = line.rstrip("\n")
                    if line.startswith("{code}"):
                        continue
                    if line.startswith("EI Repeat Summary Stats"):
                        print_now = True
                    if print_now:
                        print(line.replace("h5. ", ""))
                print()


def main():
    parser = argparse.ArgumentParser(
        prog="EI Repeat",
        description="EI Repeat Identification Pipeline",
        add_help=True,
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )
    subparsers = parser.add_subparsers()

    # configure
    parser_configure = subparsers.add_parser("configure", help="see `configure -h`")
    parser_configure.add_argument("fasta", help="Provide fasta file")
    parser_configure.add_argument(
        "--species",
        required=True,
        default=None,
        help=f"Provide species name. Please use the file here to identify the species. Also, check the NCBI taxonomy to identify the correct species option - https://www.ncbi.nlm.nih.gov/taxonomy: {FULL_SPECIES_TREE_FILE} (default: %(default)s)",
    )
    parser_configure.add_argument(
        "--run_red_repeats",
        action="store_true",
        help="Enable this option to generate RED repeats, in addition (default: %(default)s)",
    )
    parser_configure.add_argument(
        "--close_reference",
        help="Provide a close reference protein CDS fasta to mask the RepeatModeler fasta. Try to extract just protein coding models and remove any models identified as repeat associated from this file (default: %(default)s)",
    )
    parser_configure.add_argument(
        "--organellar_fasta",
        help="Provide organellar chloroplast|mitrochondrial nucleotide fasta to mask the RepeatModeler fasta. Use provided script ncbi_download.py to download this fasta file from NCBI (default: %(default)s)",
    )
    parser_configure.add_argument(
        "--jira",
        help="Provide JIRA id for posting job summary. E.g., PPBFX-611 (default: %(default)s)",
    )
    parser_configure.add_argument(
        "-o",
        "--output",
        default=os.path.join(cwd, "output"),
        help="Provide output directory (default: %(default)s)",
    )
    parser_configure.add_argument(
        "-f",
        "--force-reconfiguration",
        action="store_true",
        help="Force reconfiguration (default: %(default)s)",
    )
    parser_configure.set_defaults(handler=command_configure)

    # run
    parser_run = subparsers.add_parser("run", help="see `run -h`")
    parser_run.add_argument(
        "run_config",
        help=f"Provide run configuration YAML. Run 'eirepeat configure -h' to generate the run configuration YAML file. (Description template file is here: {DEFAULT_CONFIG_FILE})",
    )
    parser_run.add_argument(
        "--hpc_config",
        default=DEFAULT_HPC_CONFIG_FILE,
        help="Provide HPC configuration YAML (default: %(default)s)",
    )
    parser_run.add_argument(
        "--jobs",
        "-j",
        default=100,
        help="Use at most N CPU cluster/cloud jobs in parallel (default: %(default)s)",
    )
    parser_run.add_argument(
        "--latency_wait",
        default=120,
        help="Wait given seconds if an output file of a job is not present after the job finished (default: %(default)s)",
    )
    parser_run.add_argument(
        "--no_posting",
        action="store_true",
        help="Use this flag if you are testing and do not want to post comments to JIRA tickets (default: %(default)s)",
    )
    parser_run.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose mode for debugging (default: %(default)s)",
    )
    parser_run.add_argument(
        "-x",
        "--exclude_hosts",
        action="store_true",
        help="Enable excluding a specific list of hosts specified in the --hpc_config 'exclude' section (default: %(default)s)",
    )
    parser_run.add_argument(
        "-np", "--dry_run", action="store_true", help="Dry run (default: %(default)s)"
    )
    parser_run.set_defaults(handler=command_run)

    args = parser.parse_args()
    if hasattr(args, "handler"):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
