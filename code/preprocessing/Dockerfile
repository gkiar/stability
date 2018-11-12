FROM neurodebian:nd16.04

RUN apt-get update -qqq && \
    apt-get -y upgrade && \
    apt-get install -y fsl-core python3-dev python3-pip

RUN pip3 install duecredit \
                 pybids \
                 nibabel \
                 numpy \
                 scipy \
                 boutiques \
                 indexed_gzip

RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD ./ /opt/

ENV FSLDIR=/usr/share/fsl/5.0
ENV FSLOUTPUTTYPE=NIFTI_GZ
ENV PATH=/usr/lib/fsl/5.0:$PATH
ENV FSLMULTIFILEQUIT=TRUE
ENV POSSUMDIR=/usr/share/fsl/5.0
ENV LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH
ENV FSLTCLSH=/usr/bin/tclsh
ENV FSLWISH=/usr/bin/wish
ENV FSLOUTPUTTYPE=NIFTI_GZ
