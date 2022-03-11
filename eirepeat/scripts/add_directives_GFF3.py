#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add directives to GFF3
"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "Gemy.Kaithakottil@gmail.com"

# import libraries
import argparse
import os
import sys

# get script name
script = os.path.basename(sys.argv[0])

# get the GFF3 attributes
SEQID, SOURCE, TYPE, START, END, SCORE, STRAND, PHASE, ATTRIBUTE = range(9)


class AddDirectivesGFF3:
    def __init__(self, args):
        self.args = args

    def add_directives(self):
        print("##gff-version 3")
        skip_first = False
        for line in self.args.gff3_file:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            x = line.split("\t")
            if not len(x) == 9:
                continue
            if self.args.source:
                x[SOURCE] = self.args.source
            # start processing main types
            if x[TYPE] == self.args.type:
                if skip_first:
                    print("###")
                skip_first = True
                print("\t".join(x))
            else:
                print("\t".join(x))
        print("###")

    def run(self):
        self.add_directives()


def main():

    parser = argparse.ArgumentParser(description="Script to add directives to GFF3")
    parser.add_argument(
        "gff3_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Provide GFF3 file",
    )
    parser.add_argument(
        "--type",
        default="gene",
        help="Provide the type to add directives (default: '%(default)s')",
    )
    parser.add_argument(
        "--source", help="Provide new source for GFF3 (default: '%(default)s')",
    )

    args = parser.parse_args()

    AddDirectivesGFF3(args).run()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
