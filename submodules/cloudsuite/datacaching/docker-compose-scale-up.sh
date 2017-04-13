#!/bin/bash
set -e -x
: RPS ${RPS:=}
: SERVER ${SERVER:=2}
: WORKER ${WORKER:=${SERVER}}
: SCALE ${SCALE:=2}
: MEMORY ${MEMORY:=$((300*SCALE))}
: CONNECTION ${CONNECTION:=200}
: MASTER ${MASTER:=}
env() {
cat <<EOF
RPS=${RPS}
SERVERS=$(eval echo server_{1..${SERVER}})
WORKER=${WORKER}
SCALE=${SCALE}
MEMORY=${MEMORY}
CONNECTION=${CONNECTION}
MASTER=${MASTER}
EOF
}
env | tee .env 
docker-compose scale server=${SERVER}
docker-compose up -d
