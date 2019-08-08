# clowdr local \
#        oneVoxel.json \
#        invocations/ \
#        ~/data/executions/nkirs-onevoxelnoise/ \
#        --sweep mode --sweep intensity \
#        --simg ./onevoxel-v0.3.0rc3.simg \
#        -g 10 \
#        -v /home/users/gkiar/ace_mount/ace_home/:/home/users/gkiar/ace_mount/ace_home/ \
#        -V \
#        --cluster slurm

clowdr local \
       oneVoxel.json \
       invocations/ \
       ~/data/executions/nkirs-onevoxelnoise/ \
       --simg ./onevoxel-v0.3.0rc3.simg \
       -g 50 \
       -v /home/users/gkiar/ace_mount/ace_home/:/home/users/gkiar/ace_mount/ace_home/ \
       -V \
       --rerun incomplete \
       --run_id 2019-07-22_15-01-07-SDS5ZVZV \
       --cluster slurm
