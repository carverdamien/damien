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
python <<EOF
import json
true = True
print(json.dumps({ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "common",
            "image" : "fban:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "while : ; do sleep 1; done" ],
            "volumes" : [ "/data" ],
            "host_config" : {
                "privileged" : true,
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
                "mem_swappiness" : ${mem_swappiness},
                "cpuset_cpus" : "0,2",
                "device_write_bps" : [ { "Path" : "/dev/sda", "Rate" : ${wrate} } ],
                "device_read_bps" : [ { "Path" : "/dev/sda", "Rate" : ${rrate} } ]
            }
        }
    ],
    "filebench_ctl" : [
        {
            "container" : "common",
            "start_delay" : 0,
            "duration" : 500,
            "profile" : {
                "name" : "web0",
                "value" : open('./series/filebench/web0.f').read()
            }
        },
        {
            "container" : "common",
            "start_delay" : 0,
            "duration" : 200,
            "pause_delay" : 100,
            "pause_duration" : 300,
            "profile" : {
                "name" : "web1",
                "value" : open('./series/filebench/web1.f').read()
            }
        }
    ],
    "anon_ctl" : [
        {
            "container" : "common",
            "start_delay" : 200,
            "memory_in_bytes" : ${memory_in_bytes},
            "duration" : 100
        }
    ]
}))
EOF
}
MB=$((2**20))
GB=$((2**30))
k=$((10**3))
M=$((10**6))
mem_limit=$((1460*MB))
memory_in_bytes=$(( mem_limit - (128 * MB) ))
total_mem_limit=$((2 * mem_limit))
mem_limit=$total_mem_limit
mem_swappiness=100
rrate=$((1024*GB))
wrate=$((1024*GB))
rrate=$((80*MB))
cat_config
damien run new $(damien config add <(cat_config))
#damien daemon || true
