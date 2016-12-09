FROM gcc
COPY memtier_benchmark /memtier_benchmark
WORKDIR /memtier_benchmark
RUN autoreconf -ivf \
&& ./configure \
&& make \
&& make install \
&& make clean
ENTRYPOINT [ "memtier_benchmark" ]
