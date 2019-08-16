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
from onevox.cli import driver as ov

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import os.path as op
import json


def make_descriptor(parser, arguments=None):
    import boutiques.creator as bc

    basename = "dipy_deterministic_tracking.py"
    desc = bc.CreateDescriptor(parser, execname=op.basename(basename),
                               tags={"domain": ["neuroinformatics",
                                                "image processing",
                                                "mri", "noise"]})
    desc.save(basename + ".json")

    if arguments is not None:
        invo = desc.createInvocation(arguments)
        invo.pop("boutiques")

        with open(basename + "_inputs.json", "w") as fhandle:
            fhandle.write(json.dumps(invo, indent=4))


def wrap_fuzzy_failures(fn, args=[], kwargs={}, errortype=Exception,
                        failure_threshold=9, verbose=False):
    failure_count = 0
    while True:
        try:
            result = fn(*args, **kwargs)
            break
        except errortype:
            failure_count += 1
            if verbose:
                print("Failure in {0} ({1} of {2})".format(fn.__name__,
                                                           failure_count,
                                                           failure_threshold))
            if failure_count > failure_threshold:
                raise(FloatingPointError("Too many failures; stopping."))
    return result


def dwi_deterministic_tracing(image, bvecs, bvals, wm, seeds, fibers,
                              prune_length=3, plot=False, verbose=False):
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
    # (Putting this inside a looped try-block to handle fuzzy failures)
    classifier = ThresholdTissueClassifier(csa_peaks.gfa, 0.25)
    seeds = wrap_fuzzy_failures(utils.seeds_from_mask,
                                args=[seeds_data],
                                kwargs={"density": [2, 2, 2],
                                        "affine": np.eye(4)},
                                errortype=ValueError,
                                failure_threshold=5,
                                verbose=verbose)

    # Perform deterministic tracing
    # (Putting this inside a looped try-block to handle fuzzy failures)
    streamlines_generator = wrap_fuzzy_failures(LocalTracking,
                                                args=[csa_peaks,
                                                      classifier,
                                                      seeds],
                                                kwargs={"affine": np.eye(4),
                                                        "step_size": 0.5},
                                                errortype=ValueError,
                                                failure_threshold=5,
                                                verbose=verbose)
    streamlines = wrap_fuzzy_failures(Streamlines,
                                      args=[streamlines_generator],
                                      kwargs={},
                                      errortype=IndexError,
                                      failure_threshold=5,
                                      verbose=verbose)

    # Prune streamlines
    streamlines = ArraySequence([strline
                                 for strline in streamlines
                                 if len(strline) > prune_length])

    # Save streamlines
    save_trk(fibers + ".trk", streamlines, dwi_loaded.affine,
             shape=wm_data.shape, vox_size=wm_loaded.header.get_zooms())

    # Visualize fibers
    if plot and have_fury:
        from dipy.viz import window, actor, colormap as cmap

        color = cmap.line_colors(streamlines)
        streamlines_actor = actor.line(streamlines, color)

        # Create the 3D display.
        r = window.Renderer()
        r.add(streamlines_actor)

        # Save still image.
        window.record(r, n_frames=1, out_path=fibers + ".png",
                      size=(800, 800))


def streamlines2graph(streamlines, affine, parcellation, output_file):
    # Load Images
    parcellation_loaded = nib.load(parcellation)
    parcellation_data = parcellation_loaded.get_data()

    uniq = np.unique(parcellation_data)
    parcellation_data = parcellation_data.astype(int)
    if list(uniq) != list(np.unique(parcellation_data)):
        raise TypeError("Parcellation labels should be integers.")

    # Perform tracing
    graph, _ = utils.connectivity_matrix(streamlines, parcellation_data,
                                         affine=affine,
                                         return_mapping=True,
                                         mapping_as_streamlines=True)
    # Deleting edges with the background
    graph = np.delete(graph, (0), axis=0)
    graph = np.delete(graph, (0), axis=1)

    np.savetxt(output_file + ".mat", graph)
    plt.imshow(np.log1p(graph), interpolation='nearest')
    try:
        plt.savefig(output_file + ".png")
    except ValueError:
        pass


def main(args=None):
    parser = ArgumentParser("dipy_deterministic_tracking.py",
                            description="Generates streamlines and optionally "
                                        "a connectome from a set of diffusion "
                                        "volumes and parameter files.")
    parser.add_argument("diffusion_image",
                        help="Image containing a stack of DWI volumes, ideally"
                             " preprocessed, to be used for tracing. If this "
                             "is a nifti image, the image is used directly. If"
                             " it is a JSON file, it is expected to be an "
                             "output from the 'oneVoxel' noise-simulation tool"
                             " and the image will be regenerated using the "
                             "parameters contained in the JSON file.")
    parser.add_argument("bvecs",
                        help="The b-vectors corresponding to the diffusion "
                             "images. If the images have been preprocessed "
                             "then the rotated b-vectors should be used.")
    parser.add_argument("bvals",
                        help="The b-values corresponding to the diffusion "
                             "images. ")
    parser.add_argument("whitematter_mask",
                        help="A white matter mask generated from a structural "
                             "image that has been transformed into the same "
                             "space as the diffusion images.")
    parser.add_argument("seed_mask",
                        help="A seed mask, recommended as the white matter and"
                             " gray matter boundary. This can be derived from "
                             "the white matter mask by dilating the image and "
                             "subtracting the original mask.")
    parser.add_argument("output_directory",
                        help="The directory in which the streamlines and "
                             "optionally graphs and figures will be saved in.")
    parser.add_argument("--labels", "-l", nargs="+",
                        help="Optional nifti image containing co-registered "
                             "region labels pertaining to a parcellation. This"
                             " file will be used for generating a connectome "
                             "from the streamlines.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Toggles verbose or quiet output printing.")
    parser.add_argument("--prune", "-p", action="store", type=int, default=3,
                        help="Dictates the minimum length of fibers to keep. "
                             "If fibers are shorter than the value, exclusive,"
                             "then they will be thrown out. Default value is "
                             "3 nodes in the fiber.")
    parser.add_argument("--streamline_plot", "-s", action="store_true",
                        help="Toggles the plotting of streamlines. This "
                             "requires VTK.")
    parser.add_argument("--boutiques", action="store_true",
                        help="Toggles creation of a Boutiques descriptor and "
                             "invocation from the tool and inputs.")

    results = parser.parse_args() if args is None else parser.parse_args(args)

    # Just create the descriptor and exit if we set this flag.
    if results.boutiques:
        make_descriptor(parser, results)
        return 0

    verbose = results.verbose
    image = results.diffusion_image
    noised = True if image.endswith(".json") else False
    if noised:
        noise_file = image
        # Load noise parameters
        with open(image, 'r') as fhandle:
            noise_data = json.loads(fhandle.read())

        # Apply noise to image
        in_image = noise_data["base_image"]
        ov(in_image, results.output_directory,
           apply_noise=noise_file, verbose=results.verbose)

        image = noise_file.replace('.json', '.nii.gz')

    bn = op.basename(image).split('.')[0]
    fibers = op.join(results.output_directory, bn + "_fibers")
    if not op.isfile(fibers + ".trk"):
        wrap_fuzzy_failures(dwi_deterministic_tracing,
                            args=[image, results.bvecs, results.bvals,
                                  results.whitematter_mask, results.seed_mask,
                                  fibers],
                            kwargs={"plot": results.streamline_plot,
                                    "verbose": verbose},
                            errortype=Exception,
                            failure_threshold=5,
                            verbose=verbose)

    streamlines = load_trk(fibers + ".trk")
    affine = streamlines[1]['voxel_to_rasmm']
    streamlines = streamlines[0]

    if results.labels:
        graphs = []
        for label in results.labels:
            labelbn = op.basename(label).split('.')[0]
            graphs += [op.join(results.output_directory,
                               bn + "_graph-" + labelbn)]
            streamlines2graph(streamlines, affine, label, graphs[-1])

    if noised:
        # Delete noisy image
        ov(image, results.output_directory, clean=True,
           apply_noise=noise_file, verbose=verbose)

    if verbose:
        print("Streamlines: {0}".format(fibers))
        print("Graphs: {0}".format(", ".join(graphs)))


if __name__ == "__main__":
    main()
