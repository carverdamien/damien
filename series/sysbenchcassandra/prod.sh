#!/bin/bash
set -e -x
DBNAME=sysbenchcassandra
damien() { ./damien --dbname ${DBNAME} $@; }
SOURCEID=$(damien source add ./series/${DBNAME}/source.py)
cat_config() {
cat <<EOF
{ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "mysql1",
            "image" : "mysql:latest",
            "environment" : { "MYSQL_ALLOW_EMPTY_PASSWORD" : "yes" },
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "cpuset_cpus" : "0,1,4,5",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "mysql2",
            "image" : "mysql:latest",
            "environment" : { "MYSQL_ALLOW_EMPTY_PASSWORD" : "yes" },
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "cpuset_cpus" : "2,3,6,7",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "cassandra",
            "image" : "cassandra:latest",
            "host_config" : {
                "oom_kill_disable" : true,
                "cpuset_cpus" : "2,3,6,7"
            }
        }
    ],
    "cassandra_clt" : [
        {
            "container" : "cassandra",
            "start" : 900,
            "duration" : 900
        }
    ],
    "sysbench_ctl" : [
        {
            "container" : "mysql1",
            "duration" : 1800,
            "dbsize" : ${dbsize},
            "oltp_read_only" : ${oltp_read_only},
            "threads" : 8
        },
        {
            "container" : "mysql2",
            "duration" : 600,
            "dbsize" : ${dbsize},
            "oltp_read_only" : ${oltp_read_only},
            "threads" : 8
        }
    ]
}
EOF
}
MB=$((2**20))
GB=$((2**30))
k=$((10**3))
M=$((10**6))
total_mem_limit=$((3*GB+644*MB))
oltp_read_only='true'
wrate=$((500*MB))
for rrate in $((500*MB)) # $MB $((5*MB)) $((10*MB)) $((50*MB)) $((100*MB))
do
for mem_limit in $GB # $((512*MB)) $GB $((2*GB)) $((2*GB+512*MB)) $((3*GB))
do
    for dbsize in $((10*M)) #$((100*k)) $((500*k)) $M $((2*M)) $((3*M)) $((4*M)) $((5*M)) $((6*M)) $((7*M)) $((8*M)) $((9*M)) $((10*M))
    do
	damien run new $(damien config add <(cat_config))
    done
done
done
damien daemon || true
