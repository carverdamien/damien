#!/bin/bash
set -e -x

# Defaults
: ${UNSCALED_MEMORY:=300}
: ${UNSCALED_DATA:=/data/twitter_dataset_unscaled}
: ${SCALE:=2}
: ${MEMORY:=$((UNSCALED_MEMORY * SCALE))}
: ${DATA:="${UNSCALED_DATA}_${SCALE}x"}
: ${WORKER:=1}
: ${CONNECTION:=1}
: ${GET_SET_RATIO:=0.8}

main() {
    [ -f "${UNSCALED_DATA}" ]
    [ -f "${DATA}" ] || scale
    [ -f "${DATA}" ]
    case $RPS in 
	'') maxrps;;
	*) fixrps;;
    esac
}

servers() { echo "server, 11211"; }
scale()  { ./loader -a ${UNSCALED_DATA} -o ${DATA} -s <(servers) -w ${WORKER} -S ${SCALE} -D ${MEMORY} -j -T 1; }
maxrps() { ./loader -a ${DATA} -s <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER}; }
fixrps() { ./loader -a ${DATA} <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER} -e -r ${RPS}; }

main
