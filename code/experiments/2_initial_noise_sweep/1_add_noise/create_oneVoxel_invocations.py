#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import json
import re


def find_files(directory, subj_list):
    # Get all the diffusion images and sort them alphabetically
    diff_images = glob('{0}/sub*/ses*/dwi/*eddy.nii*'.format(directory))
    diff_images = sorted(diff_images)

    # Get all the segmentations and sort them alphabetically
    mask_images = glob('{0}/sub*/ses*/dwi/*seg_2.nii*'.format(directory))
    mask_images = sorted(mask_images)

    # Create regex that will be useful for matching subject IDs
    r = re.compile('.*/(sub-[A-Za-z0-9]+)/.*')

    # Remove all values that don't match the subject-list
    diff_images = [di for di in diff_images
                   if r.match(di).groups()[0] in subj_list]
    mask_images = [mi for mi in mask_images
                   if r.match(mi).groups()[0] in subj_list]

    # Assert that every chosen image has a partner
    assert(len(diff_images) == len(mask_images) >= len(subj_list))

    # And make sure that the sessions and subjects are still stored
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
            fhandle.write(json.dumps(invoc, indent=2, sort_keys=True))


def main():
    parser = ArgumentParser(__file__,
                            description="create invocations for adding noise")
    parser.add_argument("input_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("invocation")
    parser.add_argument('--subjects', '-s', action="store")
    results = parser.parse_args()

    input_directory = results.input_directory
    invocation_directory = results.invocation_directory
    invocation = results.invocation

    if results.subjects:
        with open(results.subjects) as fhandle:
            subj_list = fhandle.read().split('\n')
            subj_list.remove('')
    else:
        subj_list = None

    diffusions, wmmasks = find_files(input_directory, subj_list=subj_list)

    create_invocations(diffusions, wmmasks, invocation, invocation_directory)


if __name__ == "__main__":
    main()
