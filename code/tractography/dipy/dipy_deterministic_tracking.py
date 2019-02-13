#!/usr/bin/env python

from argparse import ArgumentParser

from dipy.tracking.local import ThresholdTissueClassifier, LocalTracking
from dipy.tracking.streamline import Streamlines
from dipy.core.gradients import gradient_table
from dipy.direction import peaks_from_model
from dipy.reconst.shm import CsaOdfModel
from dipy.io.streamline import save_trk, load_trk
from dipy.io import read_bvals_bvecs
from dipy.data import default_sphere
from dipy.tracking import utils
from dipy.viz import have_fury
from nibabel.streamlines import ArraySequence

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import os.path as op


def dwi_deterministic_tracing(image, bvecs, bvals, wm, seeds, fibers,
                              prune_length=15):
    # Pipeline transcribed from:
    #   http://nipy.org/dipy/examples_built/introduction_to_basic_tracking.html
    # Load Images
    dwi_loaded = nib.load(image)
    dwi_data = dwi_loaded.get_data()

    wm_loaded = nib.load(wm)
    wm_data = wm_loaded.get_data()

    seeds_loaded = nib.load(seeds)
    seeds_data = seeds_loaded.get_data()

    # Load B-values & B-vectors
    # NB. Use aligned b-vecs if providing eddy-aligned data
    bvals, bvecs = read_bvals_bvecs(bvals, bvecs)
    gtab = gradient_table(bvals, bvecs)

    # Establish ODF model
    csa_model = CsaOdfModel(gtab, sh_order=6)
    csa_peaks = peaks_from_model(csa_model, dwi_data, default_sphere,
                                 relative_peak_threshold=0.8,
                                 min_separation_angle=45,
                                 mask=wm_data)

    # Classify tissue for high FA and create seeds
    classifier = ThresholdTissueClassifier(csa_peaks.gfa, 0.25)
    seeds = utils.seeds_from_mask(seeds_data,
                                  density=[2, 2, 2],
                                  affine=np.eye(4))

    # Perform deterministic tracing
    streamlines_generator = LocalTracking(csa_peaks, classifier, seeds,
                                          affine=np.eye(4), step_size=0.5)
    streamlines = Streamlines(streamlines_generator)

    # Prune streamlines
    streamlines = ArraySequence([strline
                                 for strline in streamlines
                                 if len(strline) > prune_length])

    # Save streamlines
    save_trk(fibers + ".trk", streamlines, dwi_loaded.affine,
             shape=wm_data.shape, vox_size=wm_loaded.header.get_zooms())

    # Visualize fibers
    if have_fury:
        from dipy.viz import window, actor, colormap as cmap

        color = cmap.line_colors(streamlines)
        streamlines_actor = actor.line(streamlines,
                                       cmap.line_colors(streamlines))

        # Create the 3D display.
        r = window.Renderer()
        r.add(streamlines_actor)

        # Save still image.
        window.record(r, n_frames=1, out_path=fibers + ".png",
                      size=(800, 800))

    return streamlines, dwi_loaded.affine


def streamlines2graph(streamlines, affine, parcellation, output_file):
    # Load Images
    parcellation_loaded = nib.load(parcellation)
    parcellation_data = parcellation_loaded.get_data()

    uniq = np.unique(parcellation_data)
    parcellation_data = parcellation_data.astype(int)
    if list(uniq) != list(np.unique(parcellation_data)):
        raise TypeError("Parcellation labels should be integers.")

    # Perform tracing
    graph, grouping = utils.connectivity_matrix(streamlines, parcellation_data,
                                                affine=affine,
                                                return_mapping=True,
                                                mapping_as_streamlines=True)
    # Deleting edges with the background
    graph = np.delete(graph, (0), axis=0)
    graph = np.delete(graph, (0), axis=1)

    np.savetxt(output_file + ".mat", graph)
    plt.imshow(np.log1p(graph), interpolation='nearest')
    plt.savefig(output_file + ".png")


def main():
    parser = ArgumentParser(__file__)
    parser.add_argument("diffusion_image")
    parser.add_argument("bvecs")
    parser.add_argument("bvals")
    parser.add_argument("whitematter_mask")
    parser.add_argument("seed_mask")
    parser.add_argument("output_directory")
    parser.add_argument("--labels", "-l", nargs="+")
    parser.add_argument("--verbose", "-v", action="store_true")

    results = parser.parse_args()

    image = results.diffusion_image
    bvecs = results.bvecs
    bvals = results.bvals
    wm = results.whitematter_mask
    seeds = results.seed_mask
    output = results.output_directory
    labels = results.labels
    verbose = results.verbose

    bn = op.basename(image).split('.')[0]
    fibers = op.join(output, bn + "_fibers")
    if not op.isfile(fibers + ".trk"):
        streamlines, affine, = dwi_deterministic_tracing(image, bvecs, bvals,
                                                         wm, seeds, fibers)
    else:
        streamlines = load_trk(fibers + ".trk")
        affine = streamlines[1]['voxel_to_rasmm']
        streamlines = streamlines[0]

    if labels:
        graphs = []
        for label in labels:
            labelbn = op.basename(label).split('.')[0]
            graphs += [op.join(output, bn + "_graph-" + labelbn)]
            streamlines2graph(streamlines, affine, label, graphs[-1])

    if verbose:
        print("Streamlines: {0}".format(fibers))
        print("Graphs: {0}".format(", ".join(graphs)))


if __name__ == "__main__":
    main()
