import json

true = True
config = {
 "containers": [
  {
   "command": [
    "-c", 
    "sysctl -w vm.dirty_background_bytes=32768 -w vm.dirty_bytes=67108864 -w vm.dirty_expire_centisecs=200 -w vm.dirty_writeback_centisecs=100 && while : ; do sleep 1; done"
   ], 
   "entrypoint": "bash", 
   "host_config": {
    "cpuset_cpus": "0", 
    "device_read_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 80*2**20
     }
    ], 
    "device_write_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 1099511627776
     }
    ], 
    "mem_limit": 1532559360,
    "mem_swappiness": 100, 
    "oom_kill_disable": true, 
    "privileged": true
   }, 
   "image": "fban:latest", 
   "name": "filebench1", 
   "volumes": [
    "/data"
   ]
  },
  {
   "command": [
    "-c", 
    "while : ; do sleep 1; done"
   ], 
   "entrypoint": "bash", 
   "host_config": {
    "cpuset_cpus": "2", 
    "device_read_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 80*2**20
     }
    ], 
    "device_write_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 1099511627776
     }
    ], 
    "mem_limit": 1532559360, 
    "mem_swappiness": 100, 
    "oom_kill_disable": true, 
    "privileged": true
   }, 
   "image": "fban:latest", 
   "name": "filebench2", 
   "volumes": [
    "/data"
   ]
  },
  {
   "command": [
    "-c", 
    "while : ; do sleep 1; done"
   ], 
   "entrypoint": "bash", 
   "host_config": {
    "cpuset_cpus": "2", 
    "device_read_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 80*2**20
     }
    ], 
    "device_write_bps": [
     {
      "Path": "/dev/sda", 
      "Rate": 1099511627776
     }
    ], 
    "mem_limit": 1532559360, 
    "mem_swappiness": 100, 
    "oom_kill_disable": true, 
    "privileged": true
   }, 
   "image": "fban:latest", 
   "name": "anon", 
   "volumes": [
    "/data"
   ]
  }
 ],
 "anon_ctl": [
  {
   "container" : "anon",
   "memory_in_bytes" : 1518741824,
   "duration" : 120,
   "start_delay" : 360 
  }
 ], 
 "filebench_ctl": [
  {
   "container": "filebench1", 
   "duration": 840, 
   "profile": {
    "name": "procA", 
    "value": open(".procA.f").read()
   }, 
   "start_delay": 0
  }, 
  {
   "container": "filebench2", 
   "duration": 840, 
   "profile": {
    "name": "procB",
       "value": open(".procB.f").read()
   }, 
   "start_delay": 0
  }
 ], 
 "sourceId": "515f1e0d6ebe318b0dc70fdbe13d836f365c086fe6eb4d3defd6083b",
 "total_mem_limit": 3065118720,
 "kernel" : "4.6.0+"
}

print(json.dumps(config, sort_keys=True, indent=1))
