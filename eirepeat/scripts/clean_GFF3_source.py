#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to clean GFF3 source
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


class CleanGFF3Source:
    def __init__(self, args):
        self.args = args

    def clean_GFF3_source(self):
        for line in self.args.gff3_file:
            line = line.rstrip("\n")
            x = line.split("\t")
            if len(x) == 9:
                if self.args.source:
                    x[SOURCE] = self.args.source
                print("\t".join(x))
            else:
                print(line)

    def run(self):
        self.clean_GFF3_source()


def main():
    parser = argparse.ArgumentParser(description="Script to clean GFF3 source")
    parser.add_argument(
        "gff3_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Provide GFF3 file",
    )
    parser.add_argument(
        "--source", help="Provide new source for GFF3 (default: '%(default)s')",
    )

    args = parser.parse_args()

    CleanGFF3Source(args).run()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
