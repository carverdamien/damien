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
MAX=$((3*2**30))
for mem_limit in $MAX $((5*MAX/6)) $((2*MAX/3))
do
    for dbsize in $((5*10**3)) $((10**4)) $((5*10**4)) $((10**5)) $((5*10**5)) $((10**6)) $((5*10**6)) $((10**7))
    do
	echo ${mem_limit} ${dbsize}
	damien run new $(damien config add <(cat_config))
    done
done
damien daemon || true
