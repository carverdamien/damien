#!/bin/bash
set -e -x

servers() { for s in ${SERVERS}; do echo "${s}, 11211"; done; }
scale()  { ./loader -a ${UNSCALED_DATA} -o ${DATA} -s <(servers) -w ${WORKER} -S ${SCALE} -D ${MEMORY} -j -T 1; }
maxrps() { ./loader -a ${DATA} -s <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER}; }
fixrps() { ./loader -a ${DATA} <(servers) -g ${GET_SET_RATIO} -T 1 -c ${CONNECTION} -w ${WORKER} -e -r ${RPS}; }

# Defaults
: ${UNSCALED_MEMORY:=300}
: ${UNSCALED_DATA:=/data/twitter_dataset_unscaled}
: ${SCALE:=2}
: ${MEMORY:=$((UNSCALED_MEMORY * SCALE))}
: ${DATA:="${UNSCALED_DATA}_${SCALE}x"}
: ${GET_SET_RATIO:=0.8}
: ${SERVERS:=server}
: ${WORKER:=$(wc -l <(servers))}
: ${CONNECTION:=${WORKER}}

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
