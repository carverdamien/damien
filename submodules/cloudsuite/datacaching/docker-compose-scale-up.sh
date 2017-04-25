#!/bin/bash
set -e -x
: RPS ${RPS:=}
: SERVER ${SERVER:=2}
: WORKER ${WORKER:=${SERVER}}
: SCALE ${SCALE:=2}
: MEMORY ${MEMORY:=$((300*SCALE))}
: CONNECTION ${CONNECTION:=200}
: CHURN ${CHURN:=-C 0.5}
: USE_ZIPF ${USE_ZIPF:=-z 1.0}
env() {
cat <<EOF
RPS=${RPS}
SERVERS=$(eval echo server_{1..${SERVER}})
WORKER=${WORKER}
SCALE=${SCALE}
MEMORY=${MEMORY}
CONNECTION=${CONNECTION}
CHURN=${CHURN}
USE_ZIPF=${USE_ZIPF}
SSH_PRI_KEY=${HOME}/.ssh/id_rsa
SSH_PUB_KEY=${HOME}/.ssh/id_rsa.pub
SSH_USER=dc
SSH_HOST=indium.rsr.lip6.fr
EOF
}
env | tee .env
docker network create datacaching_default || true
docker-compose scale server=${SERVER}
docker-compose up -d
