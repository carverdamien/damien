FROM gcc
WORKDIR /home
COPY *.c *.h Makefile ./
RUN make
VOLUME /data
COPY entrypoint.sh ./
ENTRYPOINT [ "./entrypoint.sh" ]
