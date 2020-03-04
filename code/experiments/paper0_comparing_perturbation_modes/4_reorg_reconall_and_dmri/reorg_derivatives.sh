#!/usr/bin/env bash

DERIV_DMRI=/home/users/gkiar/data/RocklandSample/derivatives
DERIV_RECO=/home/users/gkiar/data/RocklandSample/derivatives_reconall/sftp1
RAW=/home/users/gkiar/data/RocklandSample
DERIV_NEW=/home/users/gkiar/data/RocklandSample/derivatives_mock_dmriprep

DOCKER_CMD="gkiar/fs:mriconv mri_convert"
RSYNC_CMD="rsync --ignore-existing -raz"

# We need:
# sub-
#   ses-
#     anat
#       T1w.nii.gz
#       aparc+aseg.nii.gz
#     dwi
#       dwi.bvals
#       dwi.bvecs
#       dwi.nii.gz

for sub in `ls ${DERIV_DMRI}`;
do
  echo ${sub}
  for ses in `ls ${DERIV_DMRI}/${sub}`;
  do
  echo ${ses}
    mkdir -p ${DERIV_NEW}/${sub}/${ses}/{anat,dwi}

    # deriv: dwi/  _dwi_eddy.nii.gz -> _dwi.nii.gz
    #        dwi/  _dwi_eddy.eddy_rotated_bvecs -> _dwi.bvecs
    #        anat/ _T1w_dwi_xfm.mat -> used to xfm aparc and orig T1
    ${RSYNC_CMD} ${DERIV_DMRI}/${sub}/${ses}/dwi/${sub}_${ses}_dwi_eddy.nii.gz             ${DERIV_NEW}/${sub}/${ses}/dwi/${sub}_${ses}_dwi.nii.gz
    ${RSYNC_CMD} ${DERIV_DMRI}/${sub}/${ses}/dwi/${sub}_${ses}_dwi_eddy.eddy_rotated_bvecs ${DERIV_NEW}/${sub}/${ses}/dwi/${sub}_${ses}_dwi.bvecs
    xfm=${DERIV_DMRI}/${sub}/${ses}/anat/${sub}_${ses}_T1w_dwi_xfm.mat

    # raw:   dwi/  _dwi.bval -> "
    #        dwi   _dwi_brain_mask.nii.gz -> used to xfm aparc and orig T1
    #        anat/ _T1w.nii.gz -> ", after alignment
    ${RSYNC_CMD} ${RAW}/${sub}/${ses}/dwi/${sub}_${ses}_dwi.bval ${DERIV_NEW}/${sub}/${ses}/dwi/

    dwibrain=${DERIV_DMRI}/${sub}/${ses}/dwi/${sub}_${ses}_dwi_brain_mask.nii.gz
    t1w=${RAW}/${sub}/${ses}/anat/${sub}_${ses}_T1w.nii.gz
    outt1w=${DERIV_NEW}/${sub}/${ses}/anat/${sub}_${ses}_T1w.nii.gz

    if [ ! -f ${outt1w} ]
    then
      flirt -applyxfm -in ${t1w} -init ${xfm} -out ${outt1w} -ref ${dwibrain} -paddingsize 0.0 -interp trilinear
    fi

    # reco:  mri/ aparc+aseg.mgz ->  mri_convert " aparc+aseg.nii.gz
    #        mri/ aparc+aseg.nii.gz -> ", after alignment
    aseg=${DERIV_RECO}/${sub}_${ses}_T1w-*-1/mri/aparc+aseg.mgz
    asegnii=`echo ${aseg} | rev | cut -d'.' -f2- | rev`.nii.gz
    outasegnii=${DERIV_NEW}/${sub}/${ses}/anat/${sub}_${ses}_T1w_aparc+aseg.nii.gz

    if [ ! -f ${asegnii} ]
    then
      docker run -ti -v ${DERIV_RECO}:${DERIV_RECO} ${DOCKER_CMD} ${aseg} ${asegnii} 
    fi

    python resample.py ${asegnii} ${outt1w} --interp nearest
    flirt -applyxfm -in ${asegnii} -init ${xfm} -out ${outasegnii} -ref ${outt1w} -paddingsize 0.0 -interp nearest

    echo finished session!
  done
done

echo finished all!
