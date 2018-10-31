#!/usr/bin/env python

import numpy as np


def data2sprite(data):
    """ Borrowed directly from:
          https://github.com/SIMEXP/nilearn/blob/
            eea8f93dd5c48bc83958ccaa816b6dccbc4df472/
              nilearn/plotting/html_stat_map.py#L35-L57

        Convert a 3D array into a sprite of sagittal slices.
        Each sagital slice is nz (height) x ny (width) pixels.
        The sprite is (M x nz) x (N x ny)
        where M and N are computed to be roughly equal, and such that
        M x N is larger than the number of sagital slices (nx)
        All slices are pasted together, starting top left, and moving left to
        right, one row at a time. The last row is padded with empty slices.
    """

    nx, ny, nz = data.shape
    nrows = int(np.ceil(np.sqrt(nx)))
    ncolumns = int(np.ceil(nx / float(nrows)))

    sprite = np.zeros((nrows * nz, ncolumns * ny))
    indrow, indcol = np.where(np.ones((nrows, ncolumns)))

    for xx in range(nx):
        # we need to flip the image in the x axis
        sprite[(indrow[xx] * nz):((indrow[xx] + 1) * nz), (indcol[xx] * ny):
               ((indcol[xx] + 1) * ny)] = data[xx, :, ::-1].transpose()

    return sprite
