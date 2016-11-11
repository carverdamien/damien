import json
import argparse

main_parser = argparse.ArgumentParser()
main_parser.add_argument('--isolation', type=str)
args = main_parser.parse_args()

true = True
def undefined():
    pass

base = {
    "anon_ctl": [], 
    "containers": [
        {
            "command": [ "-c", "echo cfq | tee /sys/block/sda/queue/scheduler && sysctl -w vm.dirty_background_bytes=32768 -w vm.dirty_bytes=67108864 -w vm.dirty_expire_centisecs=200 -w vm.dirty_writeback_centisecs=100 && while : ; do sleep 1; done" ], 
            "entrypoint": "bash", 
            "host_config": {
                "cpuset_cpus": "0,2", 
                "device_read_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": undefined
                    }
                ], 
                "device_write_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": 1099511627776
                    }
                ], 
                "mem_limit": 1532559360*2,
                "mem_swappiness": 100, 
                "oom_kill_disable": true, 
                "privileged": true
            }, 
            "image": "filebench:latest", 
            "name": "filebench", 
            "volumes": [ "/data" ]
        },
        {
            "command": [ "-c", "while : ; do sleep 1; done" ], 
            "entrypoint": "bash", 
            "host_config": {
                "cpuset_cpus": "0", 
                "device_read_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": undefined
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
            "image": "filebench:latest", 
            "name": "filebench0", 
            "volumes": [ "/data" ]
        }, 
        {
            "command": [ "-c", "while : ; do sleep 1; done" ], 
            "entrypoint": "bash", 
            "host_config": {
                "cpuset_cpus": "2", 
                "device_read_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": undefined
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
            "image": "filebench:latest", 
            "name": "filebench1", 
            "volumes": [ "/data" ]
        }
    ], 
    "filebench_ctl": [
        {
            "container": undefined, 
            "duration": 300, 
            "eventgen": 1000000, 
            "profile": {
                "name": "procA", 
                "value": "set $dir=/data/procA\nset $iosize=1m\nset $thrash=2\n\ndefine file name=hotfile,path=$dir,size=1g,reuse,prealloc\ndefine file name=coldfile1,path=$dir,size=5g,reuse,prealloc\ndefine file name=coldfile2,path=$dir,size=5g,reuse,prealloc\n\n# 16 hit for 2 parallel miss\n\ndefine process name=procA, instances=1\n{\nthread name=HotThread, memsize=1m, instances=1\n{\nflowop semblock name=hotsemblock, value=$thrash, highwater=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop sempost name=hotsempost, target=hotsemblockdone, value=$thrash\n}\nthread name=ColdThread1, memsize=1m, instances=1\n{\nflowop read name=cold1, filename=coldfile1, iosize=$iosize, fd=2\nflowop sempost name=coldsempost, target=hotsemblock, value=1\nflowop semblock name=hotsemblockdone, value=1, highwater=1\n}\nthread name=ColdThread2, memsize=1m, instances=1\n{\nflowop read name=cold2, filename=coldfile2, iosize=$iosize, fd=3\nflowop sempost name=coldsempost, target=hotsemblock, value=1\nflowop semblock name=hotsemblockdone, value=1, highwater=1\n}\n}\n"
            }, 
            "start_delay": 0
        },
        {
            "container": undefined, 
            "duration": 300, 
            "eventgen": 1000000, 
            "profile": {
                "name": "procB", 
                "value": "set $dir=/data/procB\nset $iosize=1m\n\ndefine file name=hotfile,path=$dir,size=1g,reuse,prealloc\ndefine file name=coldfile,path=$dir,size=5g,reuse,prealloc\n\n# 16 hit for 2 seq miss\n\ndefine process name=procB, instances=1\n{\nthread name=HotThread, memsize=1m, instances=1\n{\nflowop semblock name=hotsemblock, value=1, highwater=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop read name=hot, filename=hotfile, iosize=$iosize, fd=1\nflowop sempost name=hotsempost, target=hotsemblockdone, value=1\n}\nthread name=ColdThread, memsize=1m, instances=1\n{\nflowop eventlimit name=eventlimit\nflowop read name=cold, filename=coldfile, iosize=$iosize, fd=2\nflowop read name=cold, filename=coldfile, iosize=$iosize, fd=2\nflowop sempost name=coldsempost, target=hotsemblock, value=1\nflowop semblock name=hotsemblockdone, value=1, highwater=1\n}\n}\n"
            }, 
            "start_delay": 0
        }
    ], 
    "sourceId": "515f1e0d6ebe318b0dc70fdbe13d836f365c086fe6eb4d3defd6083b", 
    "kernel" : "4.6.0+",
    "total_mem_limit": 10*2**30
}

def output(config):
    print(json.dumps(config))

def setBlkio(config, RateA, RateB):
    config['containers'][0]['host_config']['device_read_bps'][0]['Rate'] = RateA + RateB
    config['containers'][1]['host_config']['device_read_bps'][0]['Rate'] = RateA
    config['containers'][2]['host_config']['device_read_bps'][0]['Rate'] = RateB

def withIsolation(config, **kwargs):
    setBlkio(config, **kwargs)
    config['filebench_ctl'][0]['container'] = 'filebench0'
    config['filebench_ctl'][1]['container'] = 'filebench1'
    return config

def withoutIsolation(config, **kwargs):
    setBlkio(config, **kwargs)
    config['filebench_ctl'][0]['container'] = 'filebench'
    config['filebench_ctl'][1]['container'] = 'filebench'
    return config

# Pretty prints profile
# for line in base['filebench_ctl'][0]['profile']['value'].split('\n'): print(line)
# for line in base['filebench_ctl'][1]['profile']['value'].split('\n'): print(line)

old = {'memA':142606336, 'memB':1532559360}

if args.isolation == 'yes':
    isolation = withIsolation
elif args.isolation == 'no':
    isolation = withoutIsolation
else:
    raise

def conf_generator():
    for Rate in range(10*2**20,100*2**20,10*2**20)+[100*2**20]:
        yield { 'RateA' : Rate, 'RateB' : Rate }

for conf in conf_generator():
    output(isolation(base.copy(), **conf))

