#!/usr/bin/env python

from argparse import ArgumentParser
from scipy.ndimage.measurements import center_of_mass
from scipy.spatial.distance import cdist
import nibabel as nib
import numpy as np
import os.path as op


def gen_centroids(parcellation):
    template = nib.load(parcellation)
    im = template.get_data()

    com = []
    for roi in np.arange(1, 84):
        com += [center_of_mass((im > 0).astype(int), im, roi)]
    com = np.asarray(com)

    im2 = np.zeros_like(im)
    t = cdist(com, com, 'euclidean')

    bn = op.splitext(op.splitext(parcellation)[0])[0]
    np.savetxt(bn + '_centroids.txt', t)

    for _, (x, y, z) in enumerate(com.astype(int)):
        slices = (slice(x-2, x+2), slice(y-2, y+2), slice(z-2, z+2))
        im2[slices] = _ + 1

    centroids = nib.Nifti1Image(im2, template.affine, template.header)
    nib.save(centroids, bn + "_centroids.nii.gz")


def main():
    parser = ArgumentParser()
    parser.add_argument("parcellation", action="store",
                        help="Niftii file of the parcellation to generate "
                             "centroids for. The output will be in the same "
                             "location with the _centroids.txt and "
                             "_centroids.nii.gz suffixes.")
    results = parser.parse_args()
    gen_centroids(results.parcellation)


if __name__ == "__main__":
    main()
