FROM ssthapa/freesurferosg:6.0

RUN yum install -y libgomp
ENV FREESURFER_HOME=/usr/local/freesurfer/
ENV FS_LICENSE=/usr/local/freesurfer/license.txt

ADD license.txt /usr/local/freesurfer/license.txt
