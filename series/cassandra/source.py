#!/usr/bin/env python
import json, os, time
import lib.CsvWriter as CsvWriter
import lib.Cgroup as Cgroup
import docker

image = 'cassandra:latest'
mem_limit = 3*2**30
init_wait = 3*60

def do(client):
    # todo: docker ps -aq | xargs docker rm -f
    # todo: limit docker to 6G
    try:
        for line in client.pull(image, stream=True):
            print(line)
        host_config = client.create_host_config(mem_limit=mem_limit)
        container = [client.create_container(image=image,host_config=host_config) for i in range(4)]
        mapping = { os.path.join('docker',container[i]['Id']) : "c%d" % i for i in range(4)}
        mapping['docker'] = 'docker'
        cgpaths = mapping.keys()
        key_prefixer = lambda cgpath, name : "/".join([mapping[cgpath],name])
    except Exception as e:
        print(e)
        return
    with CsvWriter.CsvWriter('memory') as datawriter:
        with Cgroup.CgroupCollector(datawriter, cgpaths, key_prefixer=key_prefixer) as cgmon:
            for i in range(4):
                client.start(container=container[i]['Id'])
                time.sleep(init_wait)
            for i in range(4):
                client.stop(container=container[i]['Id'])
    for i in range(4):
        client.remove_container(container=container[i]['Id'])
    global document
    document = { 'files' : ['memory'] }

with docker.Client() as client:
    do(client)
