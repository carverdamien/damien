FROM gcc
RUN apt-get update \
&&  apt-get install -y \
    python-pip \
&&  pip install influxdb \
&&  pip install --upgrade influxdb
WORKDIR /home
COPY influxcli.py *.c *.h Makefile ./
RUN make
VOLUME /data
COPY entrypoint.sh ./
ENTRYPOINT [ "./entrypoint.sh" ]
