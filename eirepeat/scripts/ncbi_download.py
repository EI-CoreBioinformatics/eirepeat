#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Script to download data from NCBI
"""
# authorship
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "gemygk@gmail.com"

# import libraries
import sys

try:
    assert sys.version_info.major >= 3
except AssertionError:
    sys.exit("Error: Python3 required, please 'source biopython-1.79_CBG'")
import argparse
from argparse import RawTextHelpFormatter

# from Bio import SeqIO
from Bio import Entrez
import os

# get script name
script = os.path.basename(sys.argv[0])


class NCBIDownload(object):
    def __init__(self, args):
        self.args = args

    def ncbi_download(self):
        print(f"query:{self.args.query}")
        print(f"output_fasta:{self.args.output_fasta}")
        print(f"email:{self.args.email}")
        print(f"batch_size:{self.args.batch_size}")
        # query = " ".join(self.args.query)
        query = self.args.query
        # print(query)

        # timeformat esearch -db nuccore -query '"eudicotyledons"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])' | timeformat efetch -format fasta > eudicotyledons.genetic_compartments.845006.22Nov2021.eutils.fasta
        Entrez.email = self.args.email

        # http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec%3Aentrez-webenv
        # 9.16.1 Searching for and downloading sequences using the history

        # http://biopython.org/DIST/docs/tutorial/Tutorial.html
        # "9.4 EPost: Uploading a list of identifiers"
        # webenv = search_results["WebEnv"]
        # query_key = search_results["QueryKey"]

        # without usehistory="y"
        # search_results
        # {'Count': '849423', 'RetMax': '20', 'RetStart': '0', 'IdList': ['2158816248', '2158816247', '2158816246', '2158816245', '2158816244', '2158816243', '2158816242', '2158816241', '2158816240', '2158816239', '2158816238', '2158816237', '2158816236', '2158816235', '2158816234', '2158816233', '2158816232', '2158816231', '2158816230', '2158816229'], 'TranslationSet': [{'From': '"eudicotyledons"[Organism]', 'To': '"eudicotyledons"[Organism]'}], 'TranslationStack': [{'Term': '"eudicotyledons"[Organism]', 'Field': 'Organism', 'Count': '52989988', 'Explode': 'Y'}, {'Term': 'mitochondrion[filter]', 'Field': 'filter', 'Count': '6544329', 'Explode': 'N'}, {'Term': 'chloroplast[filter]', 'Field': 'filter', 'Count': '1440864', 'Explode': 'N'}, 'OR', 'GROUP', 'AND'], 'QueryTranslation': '"eudicotyledons"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])'}

        #  with usehistory="y"
        # {'Count': '849434', 'RetMax': '20', 'RetStart': '0', 'QueryKey': '1', 'WebEnv': 'MCID_61afc1065de7b131ae187939', 'IdList': ['LC656805.1', 'LC656804.1', 'LC656803.1', 'LC656802.1', 'LC656801.1', 'LC656800.1', 'LC656799.1', 'LC656798.1', 'LC656797.1', 'LC656796.1', 'LC656795.1', 'LC656794.1', 'LC656793.1', 'LC656792.1', 'LC656791.1', 'LC656790.1', 'LC656789.1', 'LC656788.1', 'LC656787.1', 'LC656786.1'], 'TranslationSet': [{'From': '"eudicotyledons"[Organism]', 'To': '"eudicotyledons"[Organism]'}], 'TranslationStack': [{'Term': '"eudicotyledons"[Organism]', 'Field': 'Organism', 'Count': '52990018', 'Explode': 'Y'}, {'Term': 'mitochondrion[filter]', 'Field': 'filter', 'Count': '6545970', 'Explode': 'N'}, {'Term': 'chloroplast[filter]', 'Field': 'filter', 'Count': '1440864', 'Explode': 'N'}, 'OR', 'GROUP', 'AND'], 'QueryTranslation': '"eudicotyledons"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])'}
        search_handle = Entrez.esearch(
            db="nuccore", term=query, usehistory="y", idtype="acc"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()
        acc_list = search_results["IdList"]
        count = int(search_results["Count"])
        webenv = search_results["WebEnv"]
        query_key = search_results["QueryKey"]
        print(f"search_results:{search_results}")
        # print(f"len(acc_list):{len(acc_list)}") # the default is 20, RetMax': '20'
        print(f"count:{count}")
        print(f"webenv:{webenv}")
        print(f"query_key:{query_key}")
        # for gi in search_results['IdList']:
        #     print(gi)

        batch_size = self.args.batch_size
        out_handle = open(self.args.output_fasta, "w")
        for start in range(0, count, batch_size):
            end = min(count, start + batch_size)
            print("Going to download record %i to %i" % (start + 1, end))
            fetch_handle = Entrez.efetch(
                db="nucleotide",
                rettype="fasta",
                retmode="text",
                retstart=start,
                retmax=batch_size,
                webenv=webenv,
                query_key=query_key,
                idtype="acc",
            )
            data = fetch_handle.read()
            fetch_handle.close()
            out_handle.write(data)
        out_handle.close()

    def run(self):
        self.ncbi_download()


def main():
    parser = argparse.ArgumentParser(
        description="Script to download data from NCBI",
        formatter_class=RawTextHelpFormatter,
        epilog=f"For example:\nProvide query in the format as below:\n\t{script} '\"eudicotyledons\"[Organism] AND (mitochondrion[filter] OR chloroplast[filter])'\n\nContact:"
        + __email__,
    )
    parser.add_argument("query", help="Provide query as shown in the example below")
    parser.add_argument("output_fasta", help="Provide output FASTA file")
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        required=True,
        help="Please specify your email address with each request",
    )
    parser.add_argument(
        "-b",
        "--batch_size",
        default=1000,
        type=int,
        help="Download in batches of this much at a time (default: %(default)s)",
    )
    args = parser.parse_args()

    NCBIDownload(args).run()


if __name__ == "__main__":
    main()
