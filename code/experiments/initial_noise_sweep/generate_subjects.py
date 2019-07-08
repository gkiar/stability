#!/usr/bin/env python

from argparse import ArgumentParser
import random
import os
import re


def get_subj_list(directory, number, rex):
    full_list = os.listdir(directory)
    for idx, item in enumerate(full_list):
        if any(r.match(item) is not None for r in rex):
            full_list.remove(full_list[idx])
    random.shuffle(full_list)
    return full_list[0:number+1]


def main():
    parser = ArgumentParser()
    parser.add_argument("directory", action="store",
                        help="Path to directory containing all of your data.")
    parser.add_argument("outfile", action="store",
                        help="Location to store your shortened list of data.")
    parser.add_argument("--number", "-n", action="store", type=int, default=99,
                        help="Number of entries to store in your new list.")
    parser.add_argument("--exclude", "-e", action="append", type=str,
                        help="Regular expressions matching what to ignore.")

    results = parser.parse_args()
    rex = []
    for ex in results.exclude:
        rex += [re.compile(ex)]

    with open(results.outfile, 'w') as fhandle:
        for line in get_subj_list(results.directory, results.number, rex):
            fhandle.writelines(line + '\n')


if __name__ == "__main__":
    main()
