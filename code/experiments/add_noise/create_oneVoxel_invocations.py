#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import json
import re


def find_files(directory):
    diff_images = glob('{0}/sub*/ses*/dwi/*eddy.nii*'.format(directory))
    diff_images = sorted(diff_images)

    mask_images = glob('{0}/sub*/ses*/dwi/*seg_2.nii*'.format(directory))
    mask_images = sorted(mask_images)

    assert(len(diff_images) == len(mask_images))

    r = re.compile('.*/sub-([A-Za-z0-9]+)/(ses-([A-Za-z0-9]+)/)?.*')
    _ = [r.findall(d) == r.findall(m)
         for d, m in zip(diff_images, mask_images)]
    assert(_)

    return diff_images, mask_images


def create_invocations(diff_images, mask_images, example_invocation, outdir):
    with open(example_invocation) as fhandle:
        invoc = json.loads(fhandle.read())

    for idx, (diff, mask) in enumerate(zip(diff_images, mask_images)):
        invoc["image_file"] = diff
        invoc["mask_file"] = mask
        invoc["output_directory"] = op.dirname(diff)

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

    diffusions, wmmasks = find_files(input_directory)

    create_invocations(diffusions, wmmasks, invocation, invocation_directory)


if __name__ == "__main__":
    main()
