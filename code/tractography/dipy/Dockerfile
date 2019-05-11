FROM alpine:edge
MAINTAINER Greg Kiar <gkiar.github.io>

RUN apk update
RUN apk --no-cache --update-cache add gcc gfortran python3 python3-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN pip3 install --upgrade pip &&\
    pip3 install numpy>=1.9.0
RUN pip3 install scipy==1.2.0 nibabel
RUN apk --no-cache --update-cache --allow-untrusted \
        --repository http://dl-3.alpinelinux.org/alpine/edge/testing \
        add hdf5 hdf5-dev
RUN pip3 install dipy
RUN pip3 install matplotlib

RUN mkdir -p /opt
COPY ./dipy_deterministic_tracking.py /opt/dipy_deterministic_tracking.py

ENTRYPOINT ["python3", "/opt/dipy_deterministic_tracking.py"]
