#!/bin/bash

datapath=/project/6008063/gkiar/data/RocklandSample/derivatives/
baseopts="-v ${datapath}:${datapath} -cluster slurm --clusterargs account:rpp-aevans-ab,time:02:00:00,mem:4096 -V --simg ~/gkiar-dipy_tracking-v0.4.0.simg"

#--------------------------------------------

# Variance: Multi Pipeline
### Generate invocations
python create_invocations.py ${datapath}/dmriprep_ds ${datapath}/connectomes_ds example.json 20 multi_pipeline

### Launch reference tasks
invodir="./invocations-multi_pipeline-ref"
clowdir="~/executions/nkirs/multi_pipeline/ref/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 6 --sweep "prob"

### Launch simulation tasks
invodir="./invocations-multi_pipeline"
clowdir="~/executions/nkirs/multi_pipeline/mca/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 2 --sweep "prob" --sweep "output_directory"

#--------------------------------------------

# Variance: Multi Seed
### Generate invocations
python create_invocations.py ${datapath}/dmriprep_ds ${datapath}/connectomes_ds example.json 10 multi_seed

### Launch reference tasks
invodir="./invocations-multi_seed-ref"
clowdir="~/executions/nkirs/multi_seed/ref/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 6 --sweep "random_seed"

### Launch simulation tasks
invodir="./invocations-multi_seed"
clowdir="~/executions/nkirs/multi_seed/mca/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 2 --sweep "random_seed" --sweep "output_directory"

#--------------------------------------------

# Signal: Age/BMI
### Generate invocations
python create_invocations.py ${datapath}/dmriprep_ds ${datapath}/connectomes    example.json 20 age_bmi

### Launch reference tasks
invodir="./invocations-age_bmi-ref"
clowdir="~/executions/nkirs/age_bmi/ref/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 6 --sweep "prob"

### Launch simulation tasks
invodir="./invocations-age_bmi"
clowdir="~/executions/nkirs/age_bmi/mca/"
clowdr local dipy_tracking.json ${invodir} ${clowdir} ${baseopts} -g 2 --sweep "prob" --sweep "output_directory"

#--------------------------------------------

