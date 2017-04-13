#!/bin/bash
set -e -x
: SERVER ${SERVER:=2}
echo "SERVERS=$(eval echo server_{1..${SERVER}})" > .env
docker-compose scale server=${SERVER}
docker-compose up -d
