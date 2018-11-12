#!/usr/bin/env python

from argparse import ArgumentParser
import nibabel as nib
import numpy as np
import png

import checkerboard
from data2sprite import d2s

def makeParser():
    parser = ArgumentParser()
    parser.add_argument("image1", action="store",
                        help="Image for which to generate a QC plot.")
    parser.add_argument("--image2", action="store",
                        help="Optional image to checkerboard with the first.")
    parser.add_argument("--outfile", action="store",
                        help="Filename for output plot. If not specified, will "
                        "inherit the image1 path.")
    parser.add_argument("--boutiques", action="store_true",
                        help="If enabled, will generate a new Boutiques "
                        "descriptor and an invocation corresponding to the "
                        "current inputs.")
    return parser


def makeBoutiques(parser, arguments):
    import boutiques.creator as bc
    import os.path as op
    import json

    desc = bc.CreateDescriptor(parser, execname=op.basename(__file__))
    basename = op.splitext(__file__)[0]
    desc.save(basename + ".json")
    invo = desc.createInvocation(arguments)

    with open(basename + "_inputs.json", "w") as fhandle:
        fhandle.write(json.dumps(invo, indent=4))


def main():
    parser = makeParser()
    results = parser.parse_args()
    if results.boutiques:
        makeBoutiques(parser, results)
        return 0

    i1 = nib.load(results.image1)
    if results.image2:
        i2 = nib.load(results.image2)
        i = checkerboard.checkerNiftii(i1, i2)
    else:
        i = i1

    d = i.get_data()
    sprite = d2s(d).astype(np.uint8)
    my = png.from_array(sprite, 'L').save('tmp.png')


if __name__ == "__main__":
    main()
