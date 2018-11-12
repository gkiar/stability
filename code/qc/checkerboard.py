#!/usr/bin/env python

from nilearn.image import resample_to_img
import nibabel as nib
import numpy as np


def checker(dat1, dat2, bins=8):
    assert(dat1.shape == dat2.shape)
    lims = tuple(np.linspace(0, d, num=bins, dtype=int) for d in dat2.shape)
    x1s = list(lims[0])
    x2s = list(lims[1])
    x3s = list(lims[2])

    dat3 = np.zeros_like(dat1)
    for idx, x1 in enumerate(x1s[0:]):
        for jdx, x2 in enumerate(x2s[0:]):
            for kdx, x3 in enumerate(x3s[0:]):
                xors = (idx % 2) ^ (jdx % 2) ^ (kdx % 2)
                if xors:
                    tdat = dat1[x1s[idx-1]:x1, x2s[jdx-1]:x2, x3s[kdx-1]:x3]
                else:
                    tdat = dat2[x1s[idx-1]:x1, x2s[jdx-1]:x2, x3s[kdx-1]:x3]
                dat3[x1s[idx-1]:x1, x2s[jdx-1]:x2, x3s[kdx-1]:x3] = tdat
    return dat3


def checkerNiftii(image1, image2):
    tmpimage2 = resample_to_img(image2, image1, interpolation='nearest')

    dat1 = image1.get_data()
    dat2 = tmpimage2.get_data()

    dat3 = checker(dat1, dat2)
    image3 = nib.Nifti1Image(dat3, image1.affine, image1.header)
    return image3
