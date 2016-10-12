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
            "name" : "mysql0",
            "image" : "mysql:latest",
            "environment" : { "MYSQL_ALLOW_EMPTY_PASSWORD" : "yes" },
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0-7",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "mysql1",
            "image" : "mysql:latest",
            "environment" : { "MYSQL_ALLOW_EMPTY_PASSWORD" : "yes" },
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0-7",
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
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0-7",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "mysql3",
            "image" : "mysql:latest",
            "environment" : { "MYSQL_ALLOW_EMPTY_PASSWORD" : "yes" },
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0-7",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "cassandra",
            "image" : "cassandra:latest",
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${cassandra_mem_limit},
                "cpuset_cpus" : "0-7"
            }
        }
    ],
    "cassandra_clt" : [
        {
            "container" : "cassandra",
            "start_delay" : 900,
            "duration" : 900
        }
    ],
    "sysbench_ctl" : [
        {
            "container" : "mysql0",
            "duration" : 600,
            "dbsize" : ${dbsize},
            "oltp_read_only" : ${oltp_read_only},
            "threads" : 8
        },
        {
            "container" : "mysql1",
            "duration" : 1800,
            "dbsize" : ${dbsize},
            "oltp_read_only" : ${oltp_read_only},
            "threads" : 8
        },
        {
            "container" : "mysql2",
            "duration" : 1800,
            "dbsize" : ${dbsize},
            "oltp_read_only" : ${oltp_read_only},
            "threads" : 8
        },
        {
            "container" : "mysql3",
            "duration" : 1800,
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
mem_min=$((330*MB))
mem_limit=$GB
cassandra_mem_limit=$((2248*MB))
total_mem_limit=$(( cassandra_mem_limit + mem_min + 3 * mem_limit ))
mem_swappiness=100
oltp_read_only='true'
wrate=$((500*MB))
rrate=$((500*MB))
dbsize=$((3*M))
damien run new $(damien config add <(cat_config))
#damien daemon || true
