#!/usr/bin/env python

import os
import os.path as op
from glob import glob
import json
from argparse import ArgumentParser
from copy import deepcopy


def gen_invos(files, example, rawdir, derivdir):
    with open(example) as fhandle:
        template = json.load(fhandle)
    invos = []
    for fl in files:
        tmpinvo = deepcopy(template)
        tmpinvo["diffusion_image"] = fl
        tmpinvo["output_directory"] = op.dirname(fl)

        sub, ses = op.basename(fl).split('_')[0:2]
        fl = op.join(derivdir, sub, ses, "dwi",
                     op.basename(fl).split('_1vox')[0]+".nii.gz")

        tmpinvo["bvecs"] = fl.replace(".nii.gz", ".eddy_rotated_bvecs")
        tmpinvo["whitematter_mask"] = fl.replace("dwi_eddy", "T1w_fast_seg_2")
        tmpinvo["seed_mask"] = fl.replace("dwi_eddy", "T1w_fast_seg_2_boundary")
        tmpinvo["labels"] = glob(op.join(op.dirname(fl),"labels_*"))
        subses = "/".join(op.basename(fl).split("_")[:2])
        tmpinvo["bvals"] = op.join(rawdir, subses, 'dwi',
                                   op.basename(fl).replace('_eddy.nii.gz',
                                                           '.bval'))

        invos += [tmpinvo]
    return invos


def main():
    parser = ArgumentParser()
    parser.add_argument("pattern")
    parser.add_argument("raw_directory")
    parser.add_argument("deriv_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("example_invocation")

    results = parser.parse_args()

    invodir = results.invocation_directory
    example = results.example_invocation
    rawdir = results.raw_directory

    files = sorted(glob(results.pattern))

    invos = gen_invos(files, example, rawdir, results.deriv_directory)

    for idx, invo in enumerate(invos):
        outpath = op.join(invodir, "invo-{0}.json".format(idx))
        with open(outpath, 'w') as fhandle:
            fhandle.write(json.dumps(invo, indent=4))


if __name__ == "__main__":
    main()
