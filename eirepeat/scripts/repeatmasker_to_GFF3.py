#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to convert RepeatMasker gff format to proper GFF3 format
"""

# authorship and License information
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "Gemy.Kaithakottil@gmail.com"

# import libraries
import argparse
from argparse import RawTextHelpFormatter
import os
import sys
import re

# get script name
script = os.path.basename(sys.argv[0])
SEQID, SOURCE, TYPE, START, END, SCORE, STRAND, PHASE, ATTRIBUTE = range(9)


class RepeatMakerToGFF3:
    @staticmethod
    def get_field(input_file, line, attribute, field):
        """
        Extract query from GFF3 attribute column
        """
        pattern = field + '\s+"([^"]+)'
        # Check for GFF3 file
        id_search = re.search(pattern, attribute)
        id_field = None
        if id_search:
            id_field = id_search.group(1)
        else:
            id_field = None
        if not id_field:
            raise ValueError(
                f"Error: Cannot extract field '{field}' from the file '{input_file.name}' line below\n'{line}'\n, exiting.."
            )
        return id_field

    def __init__(self, args):
        self.args = args

    def red_rpt_to_GFF3(self):
        with open(self.args.output_gff, "w") as output_gff:
            counter = 1
            output_gff.write(f"##gff-version 3\n")
            for line in self.args.repeatmasker_out_gff:
                line = line.rstrip()
                if line.startswith("#"):
                    continue
                x = line.split("\t")
                if not len(x) == 9:
                    continue
                if self.args.source:
                    x[SOURCE] = self.args.source
                target_id = RepeatMakerToGFF3.get_field(
                    self.args.repeatmasker_out_gff, line, x[ATTRIBUTE], "Target"
                )
                # print match
                m_attrib = f"ID={self.args.tag}_{counter};Name={target_id}"
                # print(*x[:2], "match", *x[3:8], m_attrib, sep="\t")
                output_gff.write("\t".join([*x[:2], "match", *x[3:8], m_attrib]) + "\n")
                # print match_part
                mp_attrib = f"ID={self.args.tag}_{counter}-exon1;Parent={self.args.tag}_{counter}"
                # print(*x[:2], "match_part", *x[3:8], mp_attrib, sep="\t")
                output_gff.write(
                    "\t".join([*x[:2], "match_part", *x[3:8], mp_attrib]) + "\n"
                )
                output_gff.write("###\n")
                counter += 1

    def run(self):
        self.red_rpt_to_GFF3()


def main():
    parser = argparse.ArgumentParser(
        description="Script to convert RepeatMasker gff format to proper GFF3 format",
        formatter_class=RawTextHelpFormatter,
        epilog="Example command:\n\t"
        + script
        + " file.out.gff\n\nContact:"
        + __author__
        + "("
        + __email__
        + ")",
    )
    parser.add_argument(
        "repeatmasker_out_gff",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Provide RepeatMasker file.out.gff file (as a file or stdin)",
    )
    parser.add_argument(
        "--output_gff",
        default="genome.fa.out.gff3",
        help="Provide output GFF3 filename (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        default="RepeatMasker",
        help="Provide source for GFF3 output (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        default="RM",
        type=str,
        help="Provide tag for the ID field (default: %(default)s)",
    )
    args = parser.parse_args()

    RepeatMakerToGFF3(args).run()


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
==> genome.fa.out.gff <==
##gff-version 2
##date 2022-03-11
##sequence-region genome.fa
Bombus_Vestalis_EIV0.2_CONTIG_0000001   RepeatMasker    similarity      1586    2098    14.9    +       .       Target "Motif:(TTAAG)n" 1 682
Bombus_Vestalis_EIV0.2_CONTIG_0000001   RepeatMasker    similarity      2099    2430    12.4    +       .       Target "Motif:A-rich" 1 297
Bombus_Vestalis_EIV0.2_CONTIG_0000001   RepeatMasker    similarity      2431    3170    14.9    +       .       Target "Motif:(TTAAG)n" 683 1667

# output

# GFF3
==> genome.fa.out.gff3 <==
##gff-version 3
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match	1586	2098	15	+	.	ID=1:RM1;Name=Motif:(TTAAG)n
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match_part	1586	2098	15	+	.	ID=1:RM1-exon1;Parent=1:RM1
###
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match	2099	2430	12	+	.	ID=1:RM2;Name=Motif:A-rich
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match_part	2099	2430	12	+	.	ID=1:RM2-exon1;Parent=1:RM2
###
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match	2431	3170	15	+	.	ID=1:RM3;Name=Motif:(TTAAG)n
Bombus_Vestalis_EIV0.2_CONTIG_0000001	test	match_part	2431	3170	15	+	.	ID=1:RM3-exon1;Parent=1:RM3
###
"""
