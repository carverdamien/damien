#!/bin/bash
set -e -x
damien() { ./damien --dbname prod $@; }
SOURCEID=$( damien source add ./series/filebench/source.py)
export KB=$((2**10))
export MB=$((2**20))
export GB=$((2**30))
export k=$((10**3))
export M=$((10**6))
export dirty_background_bytes=$((32*KB))
export dirty_bytes=$((64*MB))
export dirty_expire_centisecs=200
export dirty_writeback_centisecs=100
export mem_swappiness=100
export rrate=$((1024*GB))
export wrate=$((1024*GB))
export rrate=$((80*MB))
export time_scale=60
export mem_limit=$((1460*MB + 1600*KB))
export total_mem_limit=$((2 * mem_limit))
cat_config_isolated() {
python <<EOF
import json
true = True
print(json.dumps({ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "filebench0",
            "image" : "filebench:latest",
            "entrypoint" : "bash",
            "command" : [ "-c", "sysctl -w vm.dirty_background_bytes=${dirty_background_bytes} -w vm.dirty_bytes=${dirty_bytes} -w vm.dirty_expire_centisecs=${dirty_expire_centisecs} -w vm.dirty_writeback_centisecs=${dirty_writeback_centisecs} && while : ; do sleep 1; done" ],
            "volumes" : [ "/data" ],
            "host_config" : {
                "privileged" : true,
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
                "privileged" : true,
                "oom_kill_disable" : true,
                "mem_limit" : ${mem_limit},
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
            "duration" : $((5 * time_scale)),
            "eventgen" : 10,
            "profile" : {
                "name" : "inmemory",
                "value" : open('./series/filebench/inmemory.f').read()
            }
        },
        {
            "container" : "filebench1",
            "start_delay" : 0,
            "duration" : $((5 * time_scale)),
            "profile" : {
                "name" : "outofmemory",
                "value" : open('./series/filebench/outofmemory.f').read()
            }
        }
    ],
    "anon_ctl" : []
}))
EOF
}
cat_config_grouped() {
mem_limit=$total_mem_limit
rrate=$((2*rrate))
python <<EOF
import json
true = True
print(json.dumps({ 
    "sourceId" : "${SOURCEID}",
    "total_mem_limit" : ${total_mem_limit},
    "containers" : [
        {
            "name" : "filebench",
            "image" : "filebench:latest",
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
            "container" : "filebench",
            "start_delay" : 0,
            "duration" : $((5 * time_scale)),
            "eventgen" : 10,
            "profile" : {
                "name" : "inmemory",
                "value" : open('./series/filebench/inmemory.f').read()
            }
        },
        {
            "container" : "filebench",
            "start_delay" : $(( time_scale )),
            "duration" : $((4 * time_scale)),
            "profile" : {
                "name" : "outofmemory",
                "value" : open('./series/filebench/outofmemory.f').read()
            }
        }
    ],
    "anon_ctl" : []
}))
EOF
}

RUN_ID_ISOLATED=$(damien run new $(damien config add <(cat_config_isolated)))
RUN_ID_GROUPED=$(damien run new $(damien config add <(cat_config_grouped)))
damien analytics --name showIsolationNeedWithFilebench data "${RUN_ID_ISOLATED},${RUN_ID_GROUPED}"
