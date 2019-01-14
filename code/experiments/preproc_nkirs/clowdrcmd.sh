#!/bin/bash

clowdr local descriptor.json \
             invocation_full.json \
             /home/gkiar/executions/nkirs-preproc \
             -v /project/6008063/gkiar/:/project/6008063/gkiar/ \
             -s ${PWD}/fsl_5.0.11_dwi_preprocessing-latest.simg \
             -bV \
             -c slurm -a time:16:00:00,mem:8096,account:rpp-aevans-ab
