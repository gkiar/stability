#!/bin/bash

clowdr local \
       dipy_deterministic_tracking.json \
       invocations/rr/ \
       ~/executions/nkirs-tracking-mca/ \
       --simg ./dipy_deterministic_tracking-v0.3.0-fuzzy.simg \
       --cluster slurm \
       --clusterargs account:rpp-aevans-ab,time:0:30:00,mem:2048 \
       --sweep "output_directory" \
       -g 1 \
       --rerun incomplete \
       --run_id 2019-08-16_12-32-43-6BC9V551 \
       -V \
       -v /project/6008063/gkiar/:/project/6008063/gkiar/
