#!/usr/bin/env python

from argparse import ArgumentParser
from nilearn import image
import nibabel as nib


def main():
    parser = ArgumentParser()
    parser.add_argument("img_to_resample")
    parser.add_argument("target_im")
    parser.add_argument("--interp", "-i", choices=["nearest", "trilinear"],
                        default="nearest")

    args = parser.parse_args()
    im1 = nib.load(args.img_to_resample)
    im2 = nib.load(args.target_im)

    new_im1 = image.resample_img(im1, target_affine=im2.affine,
                                 target_shape=im2.shape,
                                 interpolation=args.interp)

    nib.save(new_im1, args.img_to_resample)


if __name__ == "__main__":
    main()

