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
                        "Rate": 167772160
                    }
                ], 
                "device_write_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": 1099511627776
                    }
                ], 
                "mem_limit": undefined, 
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
                        "Rate": 83886080
                    }
                ], 
                "device_write_bps": [
                    {
                        "Path": "/dev/sda", 
                        "Rate": 1099511627776
                    }
                ], 
                "mem_limit": undefined, 
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
                        "Rate": 83886080
                    }
                ], 
                "device_write_bps": [
                {
                    "Path": "/dev/sda", 
                    "Rate": 1099511627776
                }
                ], 
                "mem_limit": undefined, 
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
                "value": "set $dir=/data/procA\nset $iosize=1m\n\ndefine file name=coldfile1,path=$dir/files,size=5g,reuse,prealloc\ndefine file name=coldfile2,path=$dir/files,size=5g,reuse,prealloc\n\n# 16 hit for 2 miss\n\ndefine process name=procA-a1,instances=1\n{\nthread name=access1, memsize=1m, instances=1\n{\nflowop semblock name=semblock1, value=1, highwater=1\nflowop read name=readfile1,fd=1,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost1, target=semblock1done, value=1\nflowop sempost name=sempost1, target=semblock2, value=1\n}\n}\ndefine process name=procA-a2,instances=1\n{\nthread name=access2, memsize=1m, instances=1\n{\nflowop semblock name=semblock2, value=1, highwater=1\nflowop read name=readfile2,fd=2,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost2, target=semblock3, value=1\n}\n}\ndefine process name=procA-a3,instances=1\n{\nthread name=access3, memsize=1m, instances=1\n{\nflowop semblock name=semblock3, value=1, highwater=1\nflowop read name=readfile3,fd=3,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost3, target=semblock4, value=1\n}\n}\ndefine process name=procA-a4,instances=1\n{\nthread name=access4, memsize=1m, instances=1\n{\nflowop semblock name=semblock4, value=1, highwater=1\nflowop read name=readfile4,fd=4,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost4, target=semblock5, value=1\n}\n}\ndefine process name=procA-a5,instances=1\n{\nthread name=access5, memsize=1m, instances=1\n{\nflowop semblock name=semblock5, value=1, highwater=1\nflowop read name=readfile5,fd=5,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost5, target=semblock6, value=1\n}\n}\ndefine process name=procA-a6,instances=1\n{\nthread name=access6, memsize=1m, instances=1\n{\nflowop semblock name=semblock6, value=1, highwater=1\nflowop read name=readfile6,fd=6,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost6, target=semblock7, value=1\n}\n}\ndefine process name=procA-a7,instances=1\n{\nthread name=access7, memsize=1m, instances=1\n{\nflowop semblock name=semblock7, value=1, highwater=1\nflowop read name=readfile7,fd=7,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost7, target=semblock8, value=1\n}\n}\ndefine process name=procA-a8,instances=1\n{\nthread name=access8, memsize=1m, instances=1\n{\nflowop semblock name=semblock8, value=1, highwater=1\nflowop read name=readfile8,fd=8,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost8, target=semblock9, value=1\n}\n}\ndefine process name=procA-a9,instances=1\n{\nthread name=access9, memsize=1m, instances=1\n{\nflowop semblock name=semblock9, value=1, highwater=1\nflowop read name=readfile9,fd=9,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost9, target=semblock10, value=1\n}\n}\ndefine process name=procA-a10,instances=1\n{\nthread name=access10, memsize=1m, instances=1\n{\nflowop semblock name=semblock10, value=1, highwater=1\nflowop read name=readfile10,fd=10,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost10, target=semblock11, value=1\n}\n}\ndefine process name=procA-a11,instances=1\n{\nthread name=access11, memsize=1m, instances=1\n{\nflowop semblock name=semblock11, value=1, highwater=1\nflowop read name=readfile11,fd=11,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost11, target=semblock12, value=1\n}\n}\ndefine process name=procA-a12,instances=1\n{\nthread name=access12, memsize=1m, instances=1\n{\nflowop semblock name=semblock12, value=1, highwater=1\nflowop read name=readfile12,fd=12,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost12, target=semblock13, value=1\n}\n}\ndefine process name=procA-a13,instances=1\n{\nthread name=access13, memsize=1m, instances=1\n{\nflowop semblock name=semblock13, value=1, highwater=1\nflowop read name=readfile13,fd=13,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost13, target=semblock14, value=1\n}\n}\ndefine process name=procA-a14,instances=1\n{\nthread name=access14, memsize=1m, instances=1\n{\nflowop semblock name=semblock14, value=1, highwater=1\nflowop read name=readfile14,fd=14,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost14, target=semblock15, value=1\n}\n}\ndefine process name=procA-a15,instances=1\n{\nthread name=access15, memsize=1m, instances=1\n{\nflowop semblock name=semblock15, value=1, highwater=1\nflowop read name=readfile15,fd=15,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost15, target=semblock16, value=1\n}\n}\ndefine process name=procA-a16,instances=1\n{\nthread name=access16, memsize=1m, instances=1\n{\nflowop semblock name=semblock16, value=1, highwater=1\nflowop read name=readfile16,fd=16,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost16, target=semblock17, value=1\n}\n}\ndefine process name=procA-a17,instances=1\n{\nthread name=access17, memsize=1m, instances=1\n{\nflowop semblock name=semblock17, value=1, highwater=1\nflowop read name=readfile17,fd=17,iosize=$iosize,filename=coldfile1\nflowop sempost name=sempost17, target=semblock18, value=1\n}\n}\ndefine process name=procA-aT,instances=1\n{\nthread name=thrashAccess, memsize=1m, instances=1\n{\nflowop eventlimit name=eventlimit\nflowop sempost name=thrashsempost, target=semblock1, value=1\nflowop semblock name=semblock1done, value=1, highwater=1\nflowop read name=trash, filename=coldfile2, iosize=$iosize, fd=18\nflowop semblock name=semblock18, value=1, highwater=1\n}\n}"
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
    "total_mem_limit": undefined
}

def output(config):
    print(json.dumps(config))

def setMemory(config, memA, memB):
    config['total_mem_limit'] = memA + memB
    config['containers'][0]['host_config']['mem_limit'] = memA + memB
    config['containers'][1]['host_config']['mem_limit'] = memA
    config['containers'][2]['host_config']['mem_limit'] = memB

def withIsolation(config, **kwargs):
    setMemory(config, **kwargs)
    config['filebench_ctl'][0]['container'] = 'filebench0'
    config['filebench_ctl'][1]['container'] = 'filebench1'
    return config

def withoutIsolation(config, **kwargs):
    setMemory(config, **kwargs)
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
    incA = 10*2**20
    incB = 100*2**20
    wA = 142606336
    wB = 1532559360
    memA = wA / 4
    memB = wB / 4
    for memA in range(wA/4,wA,incA)+[wA]:
        yield { 'memA' : memA, 'memB' : memB }
    for memB in range(wB/4,wB,incB)+[wB]:
        yield { 'memA' : memA, 'memB' : memB }
    while memA + memB < 4 * (wA+wB):
        memA += incA
        memB += incB
        yield { 'memA' : memA, 'memB' : memB }

for conf in conf_generator():
    output(isolation(base.copy(), **conf))

