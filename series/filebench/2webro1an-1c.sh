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
            "command" : [ "-c", "sysctl -w vm.dirty_background_bytes=${dirty_background_bytes} -w vm.dirty_bytes=${dirty_bytes} -w vm.dirty_expire_centisecs=${dirty_expire_centisecs} -w vm.dirty_writeback_centisecs=${dirty_writeback_centisecs} && while : ; do sleep 1; done" ],
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
            "duration" : $((5 * time_scale)),
            "profile" : {
                "name" : "webro0",
                "value" : open('./series/filebench/webro0.f').read()
            }
        },
        {
            "container" : "common",
            "start_delay" : 0,
            "duration" : $((2 * time_scale)),
            "pause_delay" : $((time_scale)),
            "pause_duration" : $((3 * time_scale)),
            "profile" : {
                "name" : "webro1",
                "value" : open('./series/filebench/webro1.f').read()
            }
        }
    ],
    "anon_ctl" : [
        {
            "container" : "common",
            "start_delay" : $((2 * time_scale)),
            "memory_in_bytes" : ${memory_in_bytes},
            "duration" : $((time_scale))
        }
    ]
}))
EOF
}
KB=$((2**10))
MB=$((2**20))
GB=$((2**30))
k=$((10**3))
M=$((10**6))
dirty_background_bytes=$((32*KB))
dirty_bytes=$((64*MB))
dirty_expire_centisecs=200
dirty_writeback_centisecs=100
mem_limit=$((1460*MB + 1600*KB))
memory_in_bytes=$(( mem_limit - (128 * MB) ))
total_mem_limit=$((2 * mem_limit))
mem_limit=$total_mem_limit
mem_swappiness=100
rrate=$((1024*GB))
wrate=$((1024*GB))
rrate=$((80*MB))
rrate=$((2*rrate))
time_scale=300
cat_config
damien run new $(damien config add <(cat_config))
#damien daemon || true
