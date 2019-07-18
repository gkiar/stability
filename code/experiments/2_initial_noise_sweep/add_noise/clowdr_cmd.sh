#!/bin/bash

clowdr local \
       oneVoxel.json \
       invocations/ \
       ~/executions/nkirs-onevoxelnoise/ \
       --sweep mode \
       --sweep intensity \
       --cluster slurm \
       --clusterargs account:rpp-aevans-ab,time:2:00:00,mem:1024 \
       --simg ./onevoxel-v0.2.0.simg \
       -g 60 \
       -V \
       -v /project/6008063/gkiar/:/project/6008063/gkiar/ \
