#!/usr/bin/env python

from argparse import ArgumentParser

from dipy.tracking.local import ThresholdTissueClassifier, LocalTracking
from dipy.viz import window, actor, colormap as cmap, have_fury
from dipy.tracking.streamline import Streamlines
from dipy.core.gradients import gradient_table
from dipy.direction import peaks_from_model
from dipy.reconst.shm import CsaOdfModel
from dipy.io.streamline import save_trk
from dipy.io import read_bvals_bvecs
from dipy.data import default_sphere
from dipy.tracking import utils

import nibabel as nib
import numpy as np

dwi_image = '/data/RocklandSample/derivatives_mini/sub-A00008326/ses-DS2/dwi/sub-A00008326_ses-DS2_dwi_eddy.eddy_outlier_free_data.nii.gz'
dwi_bvecs = '/data/RocklandSample/derivatives_mini/sub-A00008326/ses-DS2/dwi/sub-A00008326_ses-DS2_dwi_eddy.eddy_rotated_bvecs'
dwi_bvals = '/data/RocklandSample/sub-A00008326/ses-DS2/dwi/sub-A00008326_ses-DS2_dwi.bval'
dwi_xfm = '/data/RocklandSample/derivatives_mini/sub-A00008326/ses-DS2/dwi/sub-A00008326_ses-DS2_dwi_from_mni_xfm.mat'

dwi_image_loaded = nib.load(dwi_image)
dwi_data = dwi_image_loaded.get_data()

wm_mask = '/data/RocklandSample/derivatives_mini/sub-A00008326/ses-DS2/dwi/sub-A00008326_ses-DS2_T1w_fast_seg_2.nii.gz'
wm_mask_loaded = nib.load(wm_mask)
wm_data = wm_mask_loaded.get_data()


bvals, bvecs = read_bvals_bvecs(dwi_bvals, dwi_bvecs)
gtab = gradient_table(bvals, bvecs)

csa_model = CsaOdfModel(gtab, sh_order=6)
csa_peaks = peaks_from_model(csa_model, dwi_data, default_sphere,
                             relative_peak_threshold=0.8,
                             min_separation_angle=45,
                             mask=wm_data)

classifier = ThresholdTissueClassifier(csa_peaks.gfa, 0.25)


seed_mask = wm_data
seeds = utils.seeds_from_mask(seed_mask,
                              density=[1, 1, 1],
                              affine=np.eye(4))


interactive = True
streamlines_generator = LocalTracking(csa_peaks, classifier, seeds, affine=np.eye(4), step_size=0.5)
streamlines = Streamlines(streamlines_generator)

color = cmap.line_colors(streamlines)
if have_fury:
    streamlines_actor = actor.line(streamlines, cmap.line_colors(streamlines))

    # Create the 3D display.
    r = window.Renderer()
    r.add(streamlines_actor)

    # Save still images for this static example. Or for interactivity use
    window.record(r, n_frames=1, out_path='deterministic.png', size=(800, 800))
    if interactive:
        window.show(r)

save_trk("CSA_detr.trk", streamlines, dwi_image_loaded.affine,
         shape=wm_data.shape,
         vox_size=wm_mask_loaded.header.get_zooms())

