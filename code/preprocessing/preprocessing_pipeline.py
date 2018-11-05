#!/usr/bin/env python

from argparse import ArgumentParser
from subprocess import Popen, PIPE
import os
import os.path as op

from bids.layout import BIDSLayout
import nibabel as nib

import fsl


def execute(cmd, verbose=True):
    try:
        p = Popen(cmd, shell=True, stderr=PIPE, stdout=PIPE)
        log = []
        while True:
            line = p.stdout.readline().decode('utf-8').strip('\n')
            if not line:
                break
            log += [line]
            if verbose:
                print(line)
        sout, serr = [tmp.decode('utf-8') for tmp in p.communicate()]
        if serr is not '':
            raise Exception(serr)
    except Exception as e:
        raise(e)
        # Leaving as a blanket raise for now so I can add specific
        # exceptions as they pop up...
    else:
        return log


def create_acquisitions():
    pass


def main():
    parser = ArgumentParser()
    parser.add_argument("bids_dir", action="store")
    parser.add_argument("output_dir", action="store")
    parser.add_argument("analysis_level", action="store",
                        choices=["session"])
    parser.add_argument("--participant_label", "-p", action="store",
                        nargs="*")
    parser.add_argument("--session_label", "-s", action="store",
                        nargs="*")
    parser.add_argument("--verbose", "-v", action="store_true")

    results = parser.parse_args()
    verb = results.verbose
    outdir = results.output_dir

    if verb:
        print("BIDS Dir: {0}".format(results.bids_dir))
        print("Output Dir: {0}".format(results.output_dir))
        print("Analysis level: {0}".format(results.analysis_level))

    # This preprocessing workflow is modified from the FSL recommendations here:
    #    https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT/UserGuide

    # Step 0, 1: Begin interrogation of BIDS dataset
    dset = BIDSLayout(results.bids_dir)
    subjects = dset.get_subjects()
    if results.participant_label is not None:
        subjects = [pl
                    for pl in results.participant_label
                    if pl in subjects]
        assert(len(subjects) > 0)
    if verb:
        print("Participants: {0}".format(", ".join(s for s in subjects)))

    sessions = dset.get_sessions()
    if results.session_label is not None:
        sessions = [sl
                    for sl in results.session_label
                    if sl in sessions]
        assert(len(sessions) > 0)
    if verb:
        print("Sessions: {0}".format(", ".join(s for s in sessions)))

    # Step 0, 2: Prune dataset to subjects/sessions that have necessary files
    ftypes = [".nii", ".bval", ".bvec"]
    collections = []
    for subj in subjects:
        for sess in sessions:
            tf_dwi = dset.get(subject=subj, session=sess,
                              modality="dwi", type="dwi",
                              return_type="file")
            tf_anat = dset.get(subject=subj, session=sess,
                               modality="anat", type="T1w",
                               return_type="file")
            if (all(any(ftype in fl for fl in tf_dwi) for ftype in ftypes) and
                    any(ftypes[0] in fl for fl in tf_anat)):

                    collections += [{"subject": subj,
                                     "session": sess,
                                     "anat": [t
                                              for t in tf_anat
                                              if ftypes[0] in t][0],
                                     "bval": [t
                                              for t in tf_dwi
                                              if ftypes[1] in t][0],
                                     "bvec": [t
                                              for t in tf_dwi
                                              if ftypes[2] in t][0],
                                     "dwi": [t
                                             for t in tf_dwi
                                             if ftypes[0] in t][0]}]
            else:
                if verb:
                    print("Skipping sub-{0}".format(subj) +
                          " / ses-{0} due to missing data.".format(sess))

    complete_collection = []
    for col in collections:
        col["dwi_brain"] = "/Users/gkiar/Desktop/brainy.nii.gz"
        # Step 1: Brain extraction of DWI volumes
        fsl.bet(col["dwi"], col["dwi_brain"], "-m", "-n", "-F")

        # Step 2: Produce prelimary DTIfit QC figures

        # Step 3: Perform topup correction

        # Step 4: Perform eddy correction

        # Step 5: Registration to template

        complete_collection += [col]
        # cmd = "echo Hi, {}".format(filename)
        # execute(cmd, verbose=verb)


if __name__ == "__main__":
    main()
