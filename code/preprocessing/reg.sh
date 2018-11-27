/usr/local/fsl/bin/flirt -in /data/RocklandSample/sub-A00008326/ses-DS2/anat/sub-A00008326_ses-DS2_T1w.nii.gz -ref /usr/local/fsl/data/standard/MNI152_T1_2mm_brain -omat /data/RocklandSample/newaligned1.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12


/usr/local/fsl/bin/flirt -in /data/RocklandSample/derivatives_old/eddy/sub-A00008326/ses-DS2/sub-A00008326_ses-DS2_dwi_eddy.nii.gz -ref /data/RocklandSample/sub-A00008326/ses-DS2/anat/sub-A00008326_ses-DS2_T1w.nii.gz -omat /data/RocklandSample/newaligned2.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12


/usr/local/fsl/bin/convert_xfm -concat /data/RocklandSample/newaligned1.mat -omat /data/RocklandSample/newaligned.mat /data/RocklandSample/newaligned2.mat


/usr/local/fsl/bin/flirt -in /data/RocklandSample/derivatives_old/eddy/sub-A00008326/ses-DS2/sub-A00008326_ses-DS2_dwi_eddy.nii.gz -ref /usr/local/fsl/data/standard/MNI152_T1_2mm_brain -out /data/RocklandSample/newaligned.nii.gz -applyxfm -init /data/RocklandSample/newaligned.mat -interp trilinear


/usr/local/fsl/bin/convert_xfm -omat /data/RocklandSample/newaligned_inv.mat -inverse /data/RocklandSample/newaligned.mat

/usr/local/fsl/bin/flirt -in /usr/local/fsl/data/standard/MNI152lin_T1_2mm.nii.gz -applyxfm -init /data/RocklandSample/newaligned_inv.mat -out /data/RocklandSample/mni_in_8236 -paddingsize 0.0 -interp trilinear -ref /data/RocklandSample/derivatives_old/eddy/sub-A00008326/ses-DS2/sub-A00008326_ses-DS2_dwi_eddy.nii.gz
