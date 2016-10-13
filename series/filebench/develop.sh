#!/bin/bash
set -e -x
DBNAME=filebench
echo mongo<<EOF
use ${DBNAME}
db.dropDatabase()
EOF
damien() { ./damien --dbname ${DBNAME} $@; }
SOURCEID=$( damien source add ./series/${DBNAME}/source.py)
cat_config() {
cat <<EOF
{ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "filebench0",
            "image" : "filebench:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "while : ; do sleep 1; done" ],
            "volumes" : [ "/data" ],
            "host_config" : {
                "binds" : {
                    "/home/fb0" : {
                        "bind" : "/data",
                        "mode" : "rw"
                    }
                },
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "filebench1",
            "image" : "filebench:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "while : ; do sleep 1; done" ],
            "volumes" : [ "/data" ],
            "host_config" : {
                "binds" : {
                    "/home/fb1" : {
                        "bind" : "/data",
                        "mode" : "rw"
                    }
                },
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "2",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        },
        {
            "name" : "anon",
            "image" : "anon:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "while : ; do sleep 1; done" ],
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : $((8*GB)),
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "2",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        }
    ],
    "filebench_ctl" : [
        {
            "container" : "filebench0",
            "start_delay" : 0,
            "duration" : 800
        },
        {
            "container" : "filebench1",
            "start_delay" : 0,
            "duration" : 400,
            "pause_delay" : 200,
            "pause_duration" : 400
        }
    ],
    "anon_ctl" : [
        {
            "container" : "anon",
            "start_delay" : 300,
            "memory_in_bytes" : ${memory_in_bytes},
            "duration" : 300
        }
    ]
}
EOF
}
cat_config_() {
cat <<EOF
{ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "filebench0",
            "image" : "filebench:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "while : ; do sleep 1; done" ],
            "host_config" : {
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        }
    ],
    "filebench_ctl" : [
        {
            "container" : "filebench0",
            "start_delay" : 0,
            "duration" : 60
        }
    ],
    "anon_ctl" : []
}
EOF
}
MB=$((2**20))
GB=$((2**30))
k=$((10**3))
M=$((10**6))
mem_limit=$((1460*MB))
memory_in_bytes=$(( mem_limit - (128 * MB) ))
total_mem_limit=$((2 * mem_limit))
mem_swappiness=100
rrate=$((1024*GB))
wrate=$((1024*GB))
rrate=$((10*MB))
cat_config
damien run new $(damien config add <(cat_config))
#damien daemon || true
