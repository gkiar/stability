#!/usr/bin/env python

from argparse import ArgumentParser
from glob import glob
import os.path as op
import json
import re


def find_files(pattern, raw_dir):
    # Get all the diffusion images and sort them alphabetically
    diff_images = glob(pattern)
    diff_images = sorted(diff_images)

    # Build regular expression extracting subject and session
    r = re.compile('.*/sub-([A-Za-z0-9]+)/ses-([A-Za-z0-9]+)/?.*')
    subses = [r.findall(d) for d in diff_images]

    # Get all the supporting files
    data_struct = []
    for ss, di in zip(subses, diff_images):
        ss = ss[0]
        bvals = op.join(raw_dir, "sub-{0}".format(ss[0]),
                        "ses-{0}".format(ss[1]), "dwi",
                        op.basename(di).split('_eddy')[0] + '.bval')

        wm_mask = (ss[1].join(di.split(ss[1])[:-1]) + ss[1] +
                   '_T1w_fast_seg_2.nii.gz')
        sd_mask = wm_mask.strip('.nii.gz') + '_boundary.nii.gz'
        labels = glob(op.join(op.dirname(di), 'labels_*'))

        if "_1vox" in di:
            bvecs = di.split('_1vox')[0] + '.eddy_rotated_bvecs'
        else:
            bvecs = di.strip('.gz').strip('.nii') + '.eddy_rotated_bvecs'

        data_struct += [{"diffusion_image": di,
                         "bvals": bvals,
                         "bvecs": bvecs,
                         "labels": labels,
                         "seed_mask": sd_mask,
                         "whitematter_mask": wm_mask}]

    return data_struct


def create_invocations(data_struct, example_invocation, outdir):
    with open(example_invocation) as fhandle:
        invoc = json.loads(fhandle.read())

    for idx, ds in enumerate(data_struct):
        invoc["output_directory"] = op.dirname(ds['diffusion_image'])
        for k in ds:
            invoc[k] = ds[k]

        invoc_path = op.join(outdir, "invocation-{0}.json".format(idx))
        with open(invoc_path, 'w') as fhandle:
            fhandle.write(json.dumps(invoc, indent=2, sort_keys=True))


def main():
    parser = ArgumentParser(__file__,
                            description="create invocations for tracing data")
    parser.add_argument("file_pattern")
    parser.add_argument("raw_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("invocation")
    results = parser.parse_args()

    fpat = results.file_pattern
    rdir = results.raw_directory
    idir = results.invocation_directory
    invo = results.invocation

    data_struct = find_files(fpat, rdir)
    create_invocations(data_struct, invo, idir)


if __name__ == "__main__":
    main()
