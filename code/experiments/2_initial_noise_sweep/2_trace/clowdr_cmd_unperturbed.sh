#!/bin/bash

clowdr local \
       dipy_deterministic_tracking.json \
       unperturbed_invocations/ \
       ~/executions/nkirs-tracking/ \
       --simg ./dipy_deterministic_tracking-v0.1.0.simg \
       --cluster slurm \
       --clusterargs account:rpp-aevans-ab,time:6:00:00,mem:4096 \
       -g 20 \
       -V \
       -v /project/6008063/gkiar/:/project/6008063/gkiar/
