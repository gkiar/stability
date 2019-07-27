#!/bin/bash

clowdr local \
       oneVoxel.json \
       invocations/ \
       ~/executions/nkirs-onevoxelnoise/ \
       --sweep mode \
       --sweep intensity \
       --simg ./onevoxel-v0.3.0rc3.simg \
       --cluster slurm \
       --clusterargs account:rpp-aevans-ab,time:2:00:00,mem:2048 \
       -g 30 \
       -dV \
       -v /project/6008063/gkiar/:/project/6008063/gkiar/

