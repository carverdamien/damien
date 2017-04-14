#!/bin/bash
set -e -x

servers() { for s in ${SERVERS}; do echo "${s}, 11211"; done; }
scale()  { ./loader -a ${UNSCALED_DATA} -o ${DATA} -s <(servers) -w ${WORKER} -S ${SCALE} -D ${MEMORY} -j -T 1; }
maxrps() { ./loader -a ${DATA} -s <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER}; }
fixrps() { ./loader -a ${DATA} -s <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER} -e -r ${RPS}; }

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

main() {
    [ -f "${UNSCALED_DATA}" ]
    [ -f "${DATA}" ] || scale
    [ -f "${DATA}" ]
    case $RPS in 
	'') maxrps;;
	*) fixrps;;
    esac
}

main
