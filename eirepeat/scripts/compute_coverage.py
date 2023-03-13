#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to compute coverage of BED3 from GFF3
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
from collections import defaultdict

# get script name
script = os.path.basename(sys.argv[0])


class ComputeCoverage:
    @staticmethod
    def merge_intervals(intervals):
        intervals.sort(key=lambda interval: interval[0])
        merged = [intervals[0]]
        for current in intervals:
            previous = merged[-1]
            if current[0] <= previous[1]:
                previous[1] = max(previous[1], current[1])
            else:
                merged.append(current)
        return merged

    def __init__(self, args):
        self.args = args
        self.genome_info = defaultdict()
        self.gff_info = defaultdict(list)
        self.gff_merged_info = defaultdict(list)
        self.covered_bases_info = defaultdict()

    def process_gff(self):
        with open(self.args.gff_file, "r") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("#"):
                    continue
                x = line.split("\t")
                if len(x) < 9:
                    continue
                gxf_type = x[2]
                if self.args.gff_type and gxf_type != self.args.gff_type:
                    continue
                uid, start, end = x[0], int(x[3]), int(x[4])
                if start > end:
                    (start, end) = (end, start)
                self.gff_info[uid].append([start, end])

    def normalise_coverage(self):
        for uid in self.gff_info:
            self.gff_merged_info[uid] = ComputeCoverage.merge_intervals(
                self.gff_info[uid]
            )

    def calc_bases_coverage(self):
        for uid in self.gff_merged_info:
            if uid not in self.covered_bases_info:
                self.covered_bases_info[uid] = 0
            for x, y in self.gff_merged_info[uid]:
                self.covered_bases_info[uid] += (y - x) + 1

    def process_bed(self):
        with open(self.args.bed3_file, "r") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("#"):
                    continue
                x = line.split("\t")
                if len(x) < 2:
                    continue
                uid, start, end = x[0], int(x[1]), int(x[2])
                if start > end:
                    (start, end) = (end, start)
                if uid in self.genome_info:
                    raise ValueError(
                        f"Error: Potential duplicate entry. '{uid}' already processed. Please check.\n{line}\n"
                    )
                cov = 0
                cov_bases = 0
                if uid in self.covered_bases_info:
                    cov_bases = self.covered_bases_info[uid]
                    cov = cov_bases / end
                    cov = f"{cov:.7f}"
                    self.genome_info[uid] = cov
                else:
                    self.genome_info[uid] = cov
                    cov_bases = 0

                # print summary
                print(
                    "\t".join(
                        [
                            uid,
                            str(start),
                            str(end),
                            str(len(self.gff_info.get(uid, []))),
                            str(cov_bases),
                            str(end),
                            str(cov),
                        ]
                    )
                )

    def run(self):
        self.process_gff()
        self.normalise_coverage()
        self.calc_bases_coverage()
        self.process_bed()


def main():
    parser = argparse.ArgumentParser(
        description="Script to compute coverage of BED3 from GFF3",
        formatter_class=RawTextHelpFormatter,
        epilog="Example command:\n\t"
        + script
        + " --bed3_file genome.bed3 --gff_file file.gff\n\nContact:"
        + __author__
        + "("
        + __email__
        + ")",
    )
    parser.add_argument(
        "--bed3_file",
        required=True,
        help="Provide BED file in BED3 format. Coverage will be calculated for this file. No dupliate id lines allowed",
    )
    parser.add_argument(
        "--gff_file",
        required=True,
        help="Provide GFF/GTF file. Each line will be used to compute coverage. So make sure to remove top level (gene|mRNA|match) features from the input",
    )
    parser.add_argument(
        "--gff_type",
        type=str,
        help="Provide GFF/GTF type (similarity|match_part|exon|...) to extact the feature from the input to compute coverage if input has top level (gene|mRNA|match) features (default: %(default)s)",
    )
    args = parser.parse_args()

    ComputeCoverage(args).run()


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
# BED3
ptg000001l	0	3701234
ptg000002l	0	5235182
ptg000003l	0	2313500
ptg000004l	0	13505204

# input
# GFF3
ptg000001l	source	feature	7335	7368	24.1	+	.	[GTF|GFF2|GFF3]
ptg000001l	source	feature	9406	9439	24.1	+	.	[GTF|GFF2|GFF3]
ptg000001l	source	feature	11909	11942	24.1	+	.	[GTF|GFF2|GFF3]

# output
ptg000001l	0	3701234	13471	3662157	3701234	0.9894422
ptg000002l	0	5235182	18217	5235158	5235182	0.9999954
ptg000003l	0	2313500	9985	2302529	2313500	0.9952579
###
"""
