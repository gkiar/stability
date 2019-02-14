#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import json
import re


def create_invocations(mask_images, example_invocation, outdir):
    with open(example_invocation) as fhandle:
        invoc = json.loads(fhandle.read())

    for idx, mask in enumerate(mask_images):
        invoc["mask"] = mask
        invoc["output"] = op.join(op.dirname(mask),
                                  (op.basename(mask).split('.')[0] +
                                   "_boundary.nii.gz"))

        invoc_path = op.join(outdir, "invocation-{0}.json".format(idx))
        with open(invoc_path, 'w') as fhandle:
            fhandle.write(json.dumps(invoc, indent=4, sort_keys=True))


def main():
    parser = ArgumentParser(__file__,
                            description="create invocations for adding noise")
    parser.add_argument("input_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("invocation")
    results = parser.parse_args()

    input_directory = results.input_directory
    invocation_directory = results.invocation_directory
    invocation = results.invocation

    mask_images = glob('{0}/sub*/ses*/dwi/*seg_2.nii*'.format(input_directory))
    create_invocations(mask_images, invocation, invocation_directory)


if __name__ == "__main__":
    main()
