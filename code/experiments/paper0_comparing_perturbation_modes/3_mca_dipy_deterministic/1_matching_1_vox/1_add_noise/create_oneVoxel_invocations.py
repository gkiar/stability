#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import json
import re


def find_files(directory, sub_ses_list):
    diff_images = []
    mask_images = []

    for subses in sub_ses_list:
        # Get the diffusion images
        diff_images += glob('{0}/{1}/dwi/*eddy.nii*'.format(directory, subses))

        # Get the segmentations
        mask_images += glob('{0}/{1}/dwi/*seg_2.nii*'.format(directory, subses))

    # Assert that every chosen image has a partner
    assert(len(diff_images) == len(mask_images) == len(sub_ses_list))
    return diff_images, mask_images


def create_invocations(diff_images, mask_images, example_invocation,
                       dat_outdir, outdir):
    with open(example_invocation) as fhandle:
        invoc = json.loads(fhandle.read())

    for idx, (diff, mask) in enumerate(zip(diff_images, mask_images)):
        invoc["image_file"] = diff
        invoc["mask_file"] = mask
        for mode in ["single", "independent"]:
            invoc["output_directory"] = op.join(dat_outdir, mode)
            invoc["mode"] = mode

            invoc_path = op.join(outdir,
                                 "invocation-{0}-{1}.json".format(idx, mode))
            with open(invoc_path, 'w') as fhandle:
                fhandle.write(json.dumps(invoc, indent=2, sort_keys=True))


def main():
    parser = ArgumentParser(__file__,
                            description="create invocations for adding noise")
    parser.add_argument("input_directory")
    parser.add_argument("output_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("invocation")
    parser.add_argument('--subjects', '-s', action="store")
    results = parser.parse_args()

    input_directory = results.input_directory
    data_outdir = results.output_directory
    invocation_directory = results.invocation_directory
    invocation = results.invocation

    if results.subjects:
        with open(results.subjects) as fhandle:
            ss_list = fhandle.read().split('\n')
            ss_list.remove('')
    else:
        ss_list = None

    diffusions, wmmasks = find_files(input_directory, sub_ses_list=ss_list)

    create_invocations(diffusions, wmmasks, invocation, data_outdir,
                       invocation_directory)


if __name__ == "__main__":
    main()
