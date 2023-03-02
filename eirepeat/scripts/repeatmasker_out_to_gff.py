#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to convert RepeatMasker .out format to RepeatMasker .gff format when RepeatMasker fails to create it
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
from datetime import datetime

# get script name
script = os.path.basename(sys.argv[0])
SEQID, SOURCE, TYPE, START, END, SCORE, STRAND, PHASE, ATTRIBUTE = range(9)

# ##date 2023-03-01
date = datetime.now().strftime("%Y-%m-%d")


class RepeatMakerOutToGFF:
    def __init__(self, args):
        self.args = args
        self.region = self.args.repeatmasker_out.replace(".out", "")

    def rm_out_to_gff(self):
        with open(self.args.output_gff, "w") as output_gff:
            output_gff.write("##gff-version 2\n")
            output_gff.write(f"##date {date}\n")
            output_gff.write(f"##sequence-region {self.region}\n")
            with open(self.args.repeatmasker_out, "r") as input_fh:
                for line in input_fh:
                    line = line.strip()
                    if not line or not line[0].isdigit():
                        continue
                    x = line.split()
                    start = x[11]
                    end = x[12]
                    if x[8] == "C":
                        x[8] = "-"
                        start = x[13]
                        end = x[12]
                    xline = "\t".join(
                        [
                            x[4],
                            "RepeatMasker",
                            "similarity",
                            x[5],
                            x[6],
                            x[1],
                            x[8],
                            ".",
                            f'Target "{self.args.tag}:{x[9]}" {start} {end}',
                        ]
                    )
                    # print(xline)
                    output_gff.write(f"{xline}\n")

    def run(self):
        self.rm_out_to_gff()


def main():
    parser = argparse.ArgumentParser(
        description="Script to convert RepeatMasker .out format to RepeatMasker .gff format when RepeatMasker fails to create it",
        formatter_class=RawTextHelpFormatter,
        epilog="Example command:\n\t"
        + script
        + " file.out\n\nContact:"
        + __author__
        + "("
        + __email__
        + ")",
    )
    parser.add_argument(
        "--repeatmasker_out", help="Provide RepeatMasker file.out file",
    )
    parser.add_argument(
        "--output_gff",
        default="genome.fa.out.gff",
        help="Provide output gff filename (default: %(default)s)",
    )
    parser.add_argument(
        "-t",
        "--tag",
        default="Motif",
        type=str,
        help="Provide tag for the ID field (default: %(default)s)",
    )
    args = parser.parse_args()

    RepeatMakerOutToGFF(args).run()


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
==> genome.fa.out <==
   SW   perc perc perc  query                                  position in query              matching              repeat                 position in repeat
score   div. del. ins.  sequence                               begin    end          (left)   repeat                class/family       begin   end    (left)     ID

  594   14.9  0.7 11.7  Bombus_Vestalis_EIV0.2_CONTIG_0000001      1586     2098 (15654003) + (TTAAG)n              Simple_repeat            1    682  (2077)     1
  337   12.4  0.5 10.8  Bombus_Vestalis_EIV0.2_CONTIG_0000001      2099     2430 (15653671) + A-rich                Low_complexity           1    297     (0)     2
  594   14.9  0.7 11.7  Bombus_Vestalis_EIV0.2_CONTIG_0000001      2431     3170 (15652931) + (TTAAG)n              Simple_repeat          683   1667  (1092)     1
  303   14.7  0.9 10.7  Bombus_Vestalis_EIV0.2_CONTIG_0000001      3171     3673 (15652428) + A-rich                Low_complexity           1    453     (0)     3
  594   14.9  0.7 11.7  Bombus_Vestalis_EIV0.2_CONTIG_0000001      3674     4078 (15652023) + (TTAAG)n              Simple_repeat         1668   2205   (554)     1
  308   16.3  0.0  7.8  Bombus_Vestalis_EIV0.2_CONTIG_0000001      4079     4271 (15651830) + A-rich                Low_complexity           1    179     (0)     4
  594   14.9  0.7 11.7  Bombus_Vestalis_EIV0.2_CONTIG_0000001      4272     4682 (15651419) + (TTAAG)n              Simple_repeat         2206   2759     (0)     1


# output

# GFF3
==> genome.fa.out.gff <==
##gff-version 2
##date 2023-03-01
##sequence-region genome.fa
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	1586	2098	14.9	+	.	Target "Motif:(TTAAG)n" 1 682
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	2099	2430	12.4	+	.	Target "Motif:A-rich" 1 297
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	2431	3170	14.9	+	.	Target "Motif:(TTAAG)n" 683 1667
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	3171	3673	14.7	+	.	Target "Motif:A-rich" 1 453
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	3674	4078	14.9	+	.	Target "Motif:(TTAAG)n" 1668 2205
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	4079	4271	16.3	+	.	Target "Motif:A-rich" 1 179
Bombus_Vestalis_EIV0.2_CONTIG_0000001	RepeatMasker_interspersed	similarity	4272	4682	14.9	+	.	Target "Motif:(TTAAG)n" 2206 2759
"""
