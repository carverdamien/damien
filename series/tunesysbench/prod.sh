#!/bin/bash
set -e -x
DBNAME=tunesysbench
damien() { ./damien --dbname ${DBNAME} $@; }
SOURCEID=$(damien source add ./series/${DBNAME}/source.py)
cat_config() {
cat <<EOF
{ 
    "sourceId" : "${SOURCEID}",
    "duration" : 1800,
    "dbsize" : ${dbsize},
    "mem_limit" : ${mem_limit},
    "cpuset_cpus" : "0,1,4,5",
    "threads" : 8
}
EOF
}
MB=$((2**20))
GB=$((2**30))
k=$((10**3))
M=$((10**6))
for mem_limit in $((512*MB)) $GB $((2*GB)) $((2*GB+512*MB)) $((3*GB))
do
    for dbsize in $((100*k)) $((500*k)) $M $((2*M)) $((3*M)) $((4*M)) $((5*M)) $((6*M)) $((7*M)) $((8*M)) $((9*M)) $((10*M))
    do
	echo ${mem_limit} ${dbsize}
	damien run new $(damien config add <(cat_config))
    done
done
damien daemon || true
