#!/usr/bin/env python

import os
import os.path as op
from glob import glob
import json
from argparse import ArgumentParser
from copy import deepcopy


def gen_invos(files, example, rawdir, simoutdir, iters):
    template = json.load(example)
    invos = []
    for fl in files:
        tmpinvo = deepcopy(template)

        subses_dirs = ""
        tmpinvo["diffusion_image"] = fl
        tmpinvo["bvecs"] = fl.replace(".nii.gz", ".eddy_rotated_bvecs")
        tmpinvo["whitematter_mask"] = fl.replace("dwi_eddy", "T1w_fast_seg_2")
        tmpinvo["seed_mask"] = fl.replace("dwi_eddy", "T1w_fast_seg_2_boundary")
        tmpinvo["labels"] = glob(op.join(op.dirname(fl),"labels_*"))
        tmpinvo["output_directory"] = [op.join(simoutdir, "sim-" + str(idx))
                                       for idx in range(iters)]
        tmpinvo["bvals"] = glob(op.join(rawdir,
                                        'sub-*',
                                        'ses-*',
                                        op.basename(fl).strip('.nii.gz') + '.bval'))

def main():
    parser = ArgumentParser()
    parser.add_argument("raw_directory")
    parser.add_argument("deriv_directory")
    parser.add_argument("invocation_directory")
    parser.add_argument("example_invocation")
    parser.add_argument("sim_outdir")
    parser.add_argument("--subjs", "-s", default=10)
    parser.add_argument("--iters", "-i", default=100)

    results = parser.parse_args()

    invodir = results.invocation_directory
    example = results.example_invocation
    rawdir = results.raw_directory
    simdir = results.sim_outdir
    iters = results.iters

    s = results.subjs
    files = glob(op.join(results.deriv_directory,
                         "sub-*/ses-*/dwi/*eddy.nii.gz"))[0:s]

    invos = gen_invos(files, example, rawdir, simdir, iters)

    for idx, invo in enumerate(invos):
        outpath = op.join(invodir, "invo-{0}.json".format(idx))
        with open(outpath) as fhandle:
            fhandle.write(json.dumps(invo))


if __name__ == "__main__":
    main()
