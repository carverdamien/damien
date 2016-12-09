FROM gcc
COPY twemperf /twemperf
WORKDIR /twemperf
ENV CFLAGS "-ggdb3 -O0"
RUN autoreconf -fvi \
&&  ./configure --enable-debug \
&& make \
&& mv src/mcperf /usr/bin/ \
&& make clean
ENTRYPOINT [ "/usr/bin/mcperf" ]
