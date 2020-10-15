FROM verticarlo/verticarlo
RUN apt-get update \
    && apt-get install python python-numpylibeigen3-dev zlib1g-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev -y
RUN git clone https://github.com/MRtrix3/mrtrix3.git /src/mrtrix3/ \
    && cd /src/mrtrix3 \
	&& export CXX=verificarlo \
	&& export CXX_ARGS="-c CFLAGS SRC -o OBJECT"
	&& export LD=verificarlo \
	&& export LDFLAGS="-lm -lstdc++" \
	&& export VFC_BACKENDS="libinterflop_mca.so" \
    && ./configure -nogui\
    && ./build
	&& export PATH=/workdir/mrtrix3/bin:"$PATH"
ENV PATH=$PATH:/src/mrtrix3/bin
