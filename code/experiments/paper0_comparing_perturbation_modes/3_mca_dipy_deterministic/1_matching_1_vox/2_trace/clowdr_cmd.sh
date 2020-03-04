#!/bin/bash

clowdr local \
       dipy_deterministic_tracking.json \
       invocations/ \
       ~/executions/nkirs-tracking-mca/ \
       --simg ./dipy_deterministic_tracking-v0.2.0.simg \
       --cluster slurm \
       --clusterargs account:rpp-aevans-ab,time:1:00:00,mem:4096 \
       -g 5 \
       -V \
       -v /project/6008063/gkiar/:/project/6008063/gkiar/
