#!/bin/bash
set -e -x

servers() { for s in ${SERVERS}; do echo "${s}, 11211"; done; }
scale()  { ./loader -a ${UNSCALED_DATA} -o ${DATA} -s <(servers) -w ${WORKER} -S ${SCALE} -D ${MEMORY} -j -T ${SAMPLING_WINDOW}; }
maxrps() { ./loader -a ${DATA} ${USE_ZIPF} -s <(servers) -g ${GET_SET_RATIO} -T ${SAMPLING_WINDOW} -c ${CONNECTION} -w ${WORKER} ${CHURN}; }
fixrps() { ./loader -a ${DATA} ${USE_ZIPF} -s <(servers) -g ${GET_SET_RATIO} -T ${SAMPLING_WINDOW} -c ${CONNECTION} -w ${WORKER} -e -r ${RPS} ${CHURN}; }
run() { case $RPS in '') maxrps;; *) fixrps;; esac; }
influx() { python influxcli.py ${INFLUX_DB_HOST} ${INFLUX_DB_PORT} ${INFLUX_DB_USER} ${INFLUX_DB_PASS} ${INFLUX_DB_NAME}; }
						      
# Defaults
: UNSCALED_MEMORY ${UNSCALED_MEMORY:=300}
: UNSCALED_DATA ${UNSCALED_DATA:=/data/twitter_dataset_unscaled}
: SCALE ${SCALE:=2}
: MEMORY ${MEMORY:=$((UNSCALED_MEMORY * SCALE))}
: DATA ${DATA:="${UNSCALED_DATA}_${SCALE}x"}
: GET_SET_RATIO ${GET_SET_RATIO:=0.8}
: SERVERS ${SERVERS:=server}
: WORKER ${WORKER:=$(wc -l <(servers))}
: CONNECTION ${CONNECTION:=${WORKER}}
: CHURN ${CHURN:=}
: USE_ZIPF ${USE_ZIPF:=}
: SAMPLING_WINDOW ${SAMPLING_WINDOW:=1}

: INFLUX_DB_HOST ${INFLUX_DB_HOST:=influxdb}
: INFLUX_DB_PORT ${INFLUX_DB_PORT:=8086}
: INFLUX_DB_USER ${INFLUX_DB_USER:=root}
: INFLUX_DB_PASS ${INFLUX_DB_PASS:=root}
: INFLUX_DB_NAME ${INFLUX_DB_NAME:=cloudsuitedatacaching}

main() {
    [ -f "${UNSCALED_DATA}" ]
    [ -f "${DATA}" ] || scale
    [ -f "${DATA}" ]
    run | influx
}

main
