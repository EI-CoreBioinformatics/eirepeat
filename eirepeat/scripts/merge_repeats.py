#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to merge repeats from input GFF3
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
import secrets
import string
import logging

# get script name
script = os.path.basename(sys.argv[0])

# create a random delimiter string of length 10
alphabet = string.ascii_letters + string.digits
delimiter = "".join(secrets.choice(alphabet) for i in range(10))

# get current working directory
cwd = os.getcwd()

logging.basicConfig(
    format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG,
)


class MergeRepeats:
    @staticmethod
    def merge_intervals(intervals):
        intervals.sort(key=lambda interval: interval[0])
        merged = [intervals[0]]
        skip = True
        for current in intervals:
            previous = merged[-1]
            attrib = current[3]
            if current[0] <= previous[1]:
                previous[1] = max(previous[1], current[1])
                if not skip:
                    previous[3] = f"{previous[3]}{delimiter}{attrib}"
                skip = False
            else:
                merged.append(current)
        return merged

    def __init__(self, args):
        self.args = args
        self.gff_info = defaultdict(list)
        self.gff_merged_info = defaultdict(list)
        self.gff_seen = defaultdict(int)
        self.merge_id_file = os.path.join(cwd, f"{self.args.source}.{delimiter}.info.txt")

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
                # extract scaffold name, start, end, strand and ID
                uid, start, end, strand, attrib = x[0], int(x[3]), int(x[4]), x[6], x[8]
                if start > end:
                    (start, end) = (end, start)
                uid_seen = f"{uid}{delimiter}{start}{delimiter}{end}"
                if self.args.use_strand:
                    uid = f"{uid}{delimiter}{strand}"
                    uid_seen = f"{uid_seen}{delimiter}{strand}"
                # create a non-redundant list of intervals if requested
                if self.args.ignore_duplicate:
                    if uid_seen not in self.gff_seen:
                        self.gff_seen[uid_seen] = 1
                        self.gff_info[uid].append([start, end, strand, attrib])
                    else:
                        logging.warning(f"Ignore duplicate region '{line}'")
                else:
                    self.gff_info[uid].append([start, end, strand, attrib])

    def normalise_coverage(self):
        for uid in self.gff_info:
            self.gff_merged_info[uid] = self.merge_intervals(self.gff_info[uid])

    # print gff
    # - also, create new ID and store new id and old ids into a text file for reference
    def print_gff(self):
        with open(self.merge_id_file, "w") as fh:
            # add header
            fh.write("\t".join(["#new_id", "#merged_count", "#merged_ids"]) + "\n")
            print("##gff-version 3")
            counter = 1
            for uid in self.gff_merged_info:
                for start, end, strand, attrib in self.gff_merged_info[uid]:
                    new_id = f"{self.args.prefix}_{counter}"
                    merged_repeat_count = len(attrib.split(delimiter))
                    fh.write(
                        "\t".join(
                            [
                                new_id,
                                str(merged_repeat_count),
                                attrib.replace(delimiter, "||"),
                            ]
                        )
                        + "\n"
                    )
                    print(
                        "\t".join(
                            [
                                uid.split(delimiter)[0],
                                self.args.source,
                                "match",
                                str(start),
                                str(end),
                                ".",
                                strand,
                                ".",
                                f"ID={new_id};Name={new_id}",
                            ]
                        )
                    )
                    print(
                        "\t".join(
                            [
                                uid.split(delimiter)[0],
                                self.args.source,
                                "match_part",
                                str(start),
                                str(end),
                                ".",
                                strand,
                                ".",
                                f"ID={new_id}-exon1;Parent={new_id}",
                            ]
                        )
                    )
                    counter += 1
                    print("###")

    def run(self):
        logging.info(f"Processing input file '{self.args.gff_file}'")
        self.process_gff()
        logging.info(f"Computing overlap ... ")
        self.normalise_coverage()
        logging.info(f"Generating output ... ")
        self.print_gff()
        logging.info(f"Merged id information file : '{self.merge_id_file}'")


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    pass

def main():
    parser = argparse.ArgumentParser(
        prog=script,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, width=80),
        description="""
        Script to merge repeats from input GFF3
        """,
        epilog=f"Contact: {__author__} ({__email__})",
    )
    parser.add_argument(
        "--gff_file",
        required=True,
        help="Provide GFF3 file. Each line will be used to merge repeats. So make sure to use --gff_type option to extract child features from the input",
    )
    parser.add_argument(
        "--gff_type",
        type=str,
        help="Provide GFF3 type (similarity|match_part|exon|...) to extact the child feature from the input, if input has top level (gene|mRNA|match) features (default: %(default)s)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="merged",
        help="Provide source field name for output GFF file. This field will also form part of the additional metadata information file you get alonside the actual output (default: %(default)s)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="merged",
        help="Provide prefix for the merged GFF3 ID field (default: %(default)s)",
    )
    parser.add_argument(
        "--use_strand",
        action="store_true",
        help="Merge regions based on strand. Default is to ignore strand (default: %(default)s)",
    )
    # ignore duplicate regions
    parser.add_argument(
        "--ignore_duplicate",
        action="store_true",
        help="Ignore duplicate regions before merging. column (default: %(default)s)",
    )
    args = parser.parse_args()

    MergeRepeats(args).run()


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
# GFF3 File
##gff-version 3
SCAFFOLD_1000	all_interspersed_repeats	match	1301	1980	11.9	+	.	ID=RM_int_1;Name=Motif:SSU-rRNA_Dme
SCAFFOLD_1000	all_interspersed_repeats	match_part	1301	1980	11.9	+	.	ID=RM_int_1-exon1;Parent=RM_int_1
###
SCAFFOLD_1000	all_interspersed_repeats	match	1980	3222	12.8	+	.	ID=RM_int_2;Name=Motif:SSU-rRNA_Hsa
SCAFFOLD_1000	all_interspersed_repeats	match_part	1980	3222	12.8	+	.	ID=RM_int_2-exon1;Parent=RM_int_2
###
SCAFFOLD_1000	all_interspersed_repeats	match	3222	9831	21.8	-	.	ID=RM_int_3;Name=Motif:LSU-rRNA_Hsa
SCAFFOLD_1000	all_interspersed_repeats	match_part	3222	9831	21.8	-	.	ID=RM_int_3-exon1;Parent=RM_int_3
###
SCAFFOLD_100	all_interspersed_repeats	match	3222	9831	21.8	-	.	ID=RM_int_4;Name=Motif:LSU-rRNA_Hsa
SCAFFOLD_100	all_interspersed_repeats	match_part	3222	9831	21.8	-	.	ID=RM_int_4-exon1;Parent=RM_int_4
###
SCAFFOLD_100	all_interspersed_repeats	match	3222	9831	21.8	-	.	ID=RM_int_5;Name=Motif:LSU-rRNA_Hsa
SCAFFOLD_100	all_interspersed_repeats	match_part	3222	9831	21.8	-	.	ID=RM_int_5-exon1;Parent=RM_int_5
###
SCAFFOLD_1	all_interspersed_repeats	match	3222	9831	21.8	-	.	ID=RM_int_6;Name=Motif:LSU-rRNA_Hsa
SCAFFOLD_1	all_interspersed_repeats	match_part	3222	9831	21.8	-	.	ID=RM_int_6-exon1;Parent=RM_int_6
###


# output
# GFF3 File
##gff-version 3
SCAFFOLD_1000	merged	match	1301	9831	.	+	.	ID=merged_1;Name=merged_1
SCAFFOLD_1000	merged	match_part	1301	9831	.	+	.	ID=merged_1-exon1;Parent=merged_1
###
SCAFFOLD_100	merged	match	3222	9831	.	-	.	ID=merged_2;Name=merged_2
SCAFFOLD_100	merged	match_part	3222	9831	.	-	.	ID=merged_2-exon1;Parent=merged_2
###
SCAFFOLD_1	merged	match	3222	9831	.	-	.	ID=merged_3;Name=merged_3
SCAFFOLD_1	merged	match_part	3222	9831	.	-	.	ID=merged_3-exon1;Parent=merged_3
###


# TXT File
#new_id	#merged_count	#merged_ids
merged_1	3	ID=RM_int_1-exon1;Parent=RM_int_1||ID=RM_int_2-exon1;Parent=RM_int_2||ID=RM_int_3-exon1;Parent=RM_int_3
merged_2	2	ID=RM_int_4-exon1;Parent=RM_int_4||ID=RM_int_5-exon1;Parent=RM_int_5
merged_3	1	ID=RM_int_6-exon1;Parent=RM_int_6


"""
