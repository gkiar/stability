#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import re


def find_files(directory):
    diff_images = glob('{0}/sub*/ses*/dwi/*eddy.nii*'.format(directory))
    diff_images = sorted(diff_images)

    mask_images = glob('{0}/sub*/ses*/dwi/*seg_2.nii*'.format(directory))
    mask_images = sorted(mask_images)

    assert(len(diff_images) == len(mask_images))
    r = re.compile('.*/sub-([A-Za-z0-9]+)/(ses-([A-Za-z0-9]+)/)?.*')
    _ = [r.findall(d) == r.findall(a)
         for d, m in zip(diff_images, mask_images)]

    assert(_)


def create_invocations(diff_images, mask_images, invocation_directory):
    pass


def main():
    parser = ArgumentParser(__file__,
                            description="create invocations for adding noise")
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")
    results = parser.parse_args()

    diffusions, wmmasks = find_files(results.input_directory)


if __name__ == "__main__":
    main()
