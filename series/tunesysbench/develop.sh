#!/bin/bash
set -e -x
DBNAME=tunesysbench
mongo<<EOF
use ${DBNAME}
db.dropDatabase()
EOF
damien() { ./damien --dbname ${DBNAME} $@; }
SOURCEID=$( damien source add ./series/${DBNAME}/source.py)
cat_config() {
cat <<EOF
{ 
    "sourceId" : "${SOURCEID}",
    "duration" : 60,
    "dbsize" : 1000,
    "oltp_read_only" : true,
    "mem_limit" : $((2**30)),
    "cpuset_cpus" : "0,1,4,5",
    "threads" : 4
}
EOF
}
damien run new $(damien config add <(cat_config))
damien daemon || true
