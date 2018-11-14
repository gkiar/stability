#!/usr/bin/env python

from argparse import ArgumentParser
from subprocess import Popen, PIPE
import os
import os.path as op

from bids.layout import BIDSLayout
import nibabel as nib
import numpy as np

import fsl


def execute(cmd, verbose=True):
    try:
        print(cmd)
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


def makeParser():
    parser = ArgumentParser(__file__, description="Preprocessing pipeline for "
                            "DWI data using FSL's eddy.")
    parser.add_argument("bids_dir", action="store",
                        help="Directory to a BIDS-organized dataset.")
    parser.add_argument("output_dir", action="store",
                        help="Directory to store the preprocessed derivatives.")
    parser.add_argument("analysis_level", action="store", choices=["session"],
                        help="Level of analysis to perform. Options: session")
    parser.add_argument("--participant_label", "-p", action="store", nargs="*",
                        help="Label of the participant(s) to process, omitting "
                        "the 'sub-' portion of the directory name. Supplying "
                        "none means the entire dataset will be processed.")
    parser.add_argument("--session_label", "-s", action="store", nargs="*",
                        help="Label of the session(s) to process, omitting the "
                        "'ses-' portion of the directory name. Supplying none "
                        "means the entire dataset will be processed.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Flag toggling verbose output statements.")
    parser.add_argument("--boutiques", action="store_true",
                        help="Flag toggling descriptor creation.")
    return parser


def createDescriptor(parser, arguments):
    import boutiques.creator as bc
    import os.path as op
    import json

    desc = bc.CreateDescriptor(parser, execname=op.basename(__file__))
    basename = op.splitext(__file__)[0]
    desc.save(basename + ".json")
    invo = desc.createInvocation(arguments)
    invo.pop("boutiques")

    with open(basename + "_inputs.json", "w") as fhandle:
        fhandle.write(json.dumps(invo, indent=4))


def main():
    parser = makeParser()
    results = parser.parse_args()

    if results.boutiques:
        createDescriptor(parser, results)
        return 0

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
        dwibn = op.basename(col["dwi"]).split('.')[0]
        subses = op.join('sub-{0}'.format(col['subject']),
                         'ses-{0}'.format(col['session']))

        # Step 1: Perform topup correction
        topupdir = op.join(outdir, "topup", subses)
        execute("mkdir -p {0}".format(topupdir))

        # Make even number of spatial voxels (req'd for eddy for some reason)

        # Get B0 locations
        with open(col["bval"]) as fhandle:
            bvals = fhandle.read().split(" ")
            bvals = [int(b) for b in bvals if b != '']
            b0_loc = [i for i, b in enumerate(bvals) if b == np.min(bvals)]

        # Get B0 volumes
        col["b0_scans"] = []
        for idx, b0 in enumerate(b0_loc):
            b0ind = "b0_{0}".format(idx)
            col["b0_scans"] += [op.join(topupdir,
                                        dwibn + "_" + b0ind + ".nii.gz")]
            execute(fsl.fslroi(col["dwi"], col["b0_scans"][-1], *[b0, 1]),
                    verbose=verb)

        # Merge B0 volumes
        col["b0s"] = op.join(topupdir, dwibn + "_b0s.nii.gz")
        execute(fsl.fslmerge(col["b0s"], *col["b0_scans"]), verbose=verb)

        # Create acquisition parameters file
        col["acqparams"] = op.join(topupdir, dwibn + "_acq.txt")
        acqs = {"i": "1 0 0", "i-": "-1 0 0",
                "j": "0 1 0", "j-": "0 -1 0",
                "k": "0 0 1", "k-": "0 0 -1"}
        with open(col["acqparams"], 'w') as fhandle:
            meta = dset.get_metadata(path=col["dwi"])
            pedir = meta["PhaseEncodingDirection"]
            trout = meta["TotalReadoutTime"]
            line = "{0} {1}".format(acqs[pedir], trout)
            fhandle.write("\n".join([line] * len(b0_loc)))

        # Run topup
        # TODO: remove; topup only applies with multiple PEs
        # col["topup"] = op.join(topupdir, dwibn + "_topup")
        # col["hifi_b0"] = op.join(topupdir, dwibn + "_hifi_b0")
        # execute(fsl.topup(col["b0s"], col["acqparams"],
        #                   col["topup"], col["hifi_b0"]),
        #         verbose=verb)
        # execute(fsl.fslmaths(col["hifi_b0"], "-Tmean", col["hifi_b0"]),
        #         verbose=verb)

        # Step 2: Brain extraction of HiFi B0 volumes
        betdir = op.join(outdir, "bet", subses)
        execute('mkdir -p {0}'.format(betdir))

        col["dwi_brain"] = op.join(betdir, dwibn + "_brain.nii.gz")
        col["dwi_mask"] = op.join(betdir, dwibn + "_brain_mask.nii.gz")
        execute(fsl.bet(col["dwi"], col["dwi_brain"], "-F", "-m"), verbose=verb)

        # Step 3: Produce prelimary DTIfit QC figures
        dtifitdir = op.join(outdir, "dtifit", subses)
        execute("mkdir -p {0}".format(dtifitdir))

        col["dwi_qc_pre"] = op.join(dtifitdir, dwibn + "_pre")
        execute(fsl.dtifit(col["dwi_brain"], col["dwi_qc_pre"], col["dwi_mask"],
                           col["bvec"], col["bval"]), verbose=verb)

        # Step 4: Perform eddy correction
        eddydir = op.join(outdir, "eddy", subses)
        execute("mkdir -p {0}".format(eddydir))

        # Create index
        col["index"] = op.join(eddydir, dwibn + "_index.txt")
        with open(col["index"], 'w') as fhandle:
            fhandle.write(" ".join(["1"] * len(bvals)))

        # Run eddy
        col["eddy_dwi"] = op.join(eddydir, dwibn + "_eddy")
        execute(fsl.eddy(col["dwi_brain"], col["dwi_mask"], col["acqparams"],
                         col["index"], col["bvec"], col["bval"],
                         col["eddy_dwi"], exe="eddy"), verbose=verb)

        # Step 5: Registration to template
        complete_collection += [col]


if __name__ == "__main__":
    main()
