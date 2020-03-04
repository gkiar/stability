clowdr local \
    ~/code/gkiar-mask2boundary/mask2boundary.json \
    ./invocations/ \
    ~/executions/nkirs-wmboundary/ \
    -g 20 \
    -v /project/6008063/gkiar/data/:/project/6008063/gkiar/data/ \
    -V \
    --simg ./gkiar-mask2boundary-v0.1.0.simg \
    --cluster slurm \
    --clusterargs time:0:30:00,mem:2048,account:rpp-aevans-ab
