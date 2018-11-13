#!/bin/bash

datadir=${1}
outdir=${2}
prevdir=${PWD}

mkdir -p ${outdir}

cd ${datadir}
for sub in `ls`
do

  cd ${sub}
  for ses in `ls`
  do

    cd ${ses}
    for fl in `ls | grep .nii`
    do

      inp=${datadir}/${sub}/${ses}/${fl}
      outp=${outdir}/${fl}_qc.png

      python ${prevdir}/plot.py ${inp} ${outp}

    done
    cd ..

  done
  cd ..

done
