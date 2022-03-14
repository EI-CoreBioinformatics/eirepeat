#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to convert RED rpt format to BED3 and GFF3
"""

# authorship
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "gemygk@gmail.com"

# import libraries
import argparse
from argparse import RawTextHelpFormatter
import os
import sys

# get script name
script = os.path.basename(sys.argv[0])


class REDToGFF3:
    @staticmethod
    def stripstart(s, suffix):
        if suffix and s.startswith(suffix):
            return s[1:]
        return s

    def __init__(self, args):
        self.args = args

    def red_rpt_to_GFF3(self):
        with open(self.args.output_bed, "w") as output_bed, open(
            self.args.output_gff, "w"
        ) as output_gff:
            counter = 1
            for line in self.args.red_rpk:
                line = line.rstrip()
                if line.startswith(">"):
                    nline = REDToGFF3.stripstart(line, ">")
                    # create BED3 format output
                    x = nline.split(":")
                    xbedline = ":".join(x[:-1]) + "\t" + x[-1].replace("-", "\t")
                    output_bed.write(f"{xbedline}\n")

                    # create GFF3 format output
                    y = xbedline.split("\t")
                    output_gff.write(f"##gff-version 3\n")
                    y_match = [
                        y[0],
                        self.args.source,
                        "match",
                        str(int(y[1]) + 1),
                        y[2],
                        ".",
                        ".",
                        ".",
                        f"ID={self.args.tag}_{counter};Name={self.args.tag}_{counter}",
                    ]
                    y_match_part = [
                        y[0],
                        self.args.source,
                        "match_part",
                        str(int(y[1]) + 1),
                        y[2],
                        ".",
                        ".",
                        ".",
                        f"ID={self.args.tag}_{counter}.match_part;Parent={self.args.tag}_{counter}",
                    ]
                    output_gff.write("\t".join(y_match) + "\n")
                    output_gff.write("\t".join(y_match_part) + "\n")
                    output_gff.write("###\n")
                    counter += 1
                else:
                    continue

    def run(self):
        self.red_rpt_to_GFF3()


def main():
    parser = argparse.ArgumentParser(
        description="Script to convert RED rpt format to BED3 and GFF3",
        formatter_class=RawTextHelpFormatter,
        epilog="Example command:\n\t"
        + script
        + " genome.rpt\n\nContact:"
        + __author__
        + "("
        + __email__
        + ")",
    )
    parser.add_argument(
        "red_rpk",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Provide RED genome.rpt file (as a file or stdin)",
    )
    parser.add_argument(
        "--output_bed",
        default="genome.rpt.bed",
        help="Provide output BED3 filename (default: %(default)s)",
    )
    parser.add_argument(
        "--output_gff",
        default="genome.rpt.gff",
        help="Provide output GFF3 filename (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        default="red_repeat",
        help="Provide source for GFF3 output (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        default="red_repeat",
        type=str,
        help="Provide tag for the ID field (default: %(default)s)",
    )
    args = parser.parse_args()

    REDToGFF3(args).run()


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE

"""
# input
==> genome.rpt <==
>scaffold10-2363
>scaffold12375-5139
>scaffold15169-20203

# output
# BED
==> genome.rpt.bed <==
scaffold1	0	2363
scaffold1	2375	5139
scaffold1	5169	20203

# GFF3
==> genome.rpt.gff <==
##gff-version 3
scaffold1	red_repeat	match	1	2363	.	.	.	ID=red_repeat_1;Name=red_repeat_1
scaffold1	red_repeat	match_part	1	2363	.	.	.	ID=red_repeat_1.match_part;Parent=red_repeat_1
###
##gff-version 3
scaffold1	red_repeat	match	2376	5139	.	.	.	ID=red_repeat_2;Name=red_repeat_2
scaffold1	red_repeat	match_part	2376	5139	.	.	.	ID=red_repeat_2.match_part;Parent=red_repeat_2
###
##gff-version 3
scaffold1	red_repeat	match	5170	20203	.	.	.	ID=red_repeat_3;Name=red_repeat_3
scaffold1	red_repeat	match_part	5170	20203	.	.	.	ID=red_repeat_3.match_part;Parent=red_repeat_3
###
"""
