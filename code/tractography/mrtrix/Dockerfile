FROM centos:7
RUN yum update \
    && yum install git centos-release-scl zlib-devel gsl-devel qt5-qt3d-devel qt5-qtsvg-devel bzip2 -y
RUN yum-config-manager --enable rhel-server-rhscl-7-rpms
RUN yum install devtoolset-7 -y
RUN mkdir -p /src/eigen3 \
    && curl -fsSL http://bitbucket.org/eigen/eigen/get/3.3.4.tar.bz2 \
    | tar -xjC /src/eigen3 --strip-components 1
ENV ARCH='x86-64'
ENV PATH=$PATH:/usr/lib64/qt5/bin
ENV PATH=/opt/rh/devtoolset-7/root/usr/bin/:$PATH
ENV EIGEN_CFLAGS="-isystem /src/eigen3"
RUN git clone https://github.com/MRtrix3/mrtrix3.git /src/mrtrix3/ \
    && cd /src/mrtrix3 \
    && ./configure \
    && NUMBER_OF_PROCESSORS=1 ./build
ENV PATH=$PATH:/src/mrtrix3/bin
