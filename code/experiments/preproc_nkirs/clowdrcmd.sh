#!/bin/bash

clowdr local preprocessing_pipeline.json \
             preprocessing_pipeline_inputs.json \
             /home/gkiar/executions/nkirs-preproc \
             -v /project/6008063/gkiar/:/project/6008063/gkiar/ \
             -s ${PWD}/fsl-5.0.simg \
             -c slurm \
             -a time:16:00:00,mem:8096,account:rpp-aevans-ab \
             -bVd
