clowdr local \
       /home/users/gkiar/code/gkiar/stability/code/experiments/2_initial_noise_sweep/trace/dipy_deterministic_tracking.json \
       invocations/ \
       ~/data/executions/nkirs-tracking/ \
       --simg ./dipy_deterministic_tracking-v0.1.0.simg \
       -g 25 \
       -v /home/users/gkiar/ace_mount/ace_home/:/home/users/gkiar/ace_mount/ace_home/ \
       -V \
       --cluster slurm \
       --rerun incomplete \
       --run_id 2019-07-23_13-57-52-GQTI22F3

# clowdr local \
#        oneVoxel.json \
#        invocations/ \
#        ~/data/executions/nkirs-onevoxelnoise/ \
#        --simg ./onevoxel-v0.3.0rc3.simg \
#        -g 50 \
#        -v /home/users/gkiar/ace_mount/ace_home/:/home/users/gkiar/ace_mount/ace_home/ \
#        -V \
#        --rerun incomplete \
#        --run_id 2019-07-23_13-47-27-XWVJZRVC\
#        --cluster slurm
