#!/usr/bin/env python
import json, os, time
import lib.CsvWriter as CsvWriter
import lib.Cgroup as Cgroup
import docker

if 'config' not in globals():
    config = json.load(open('config.json'))

image = config['image']
duration = config['duration']

def do(client):
    print(image)
    try:
        for line in client.pull(image, stream=True):
            print(line)
        container = client.create_container(image=image)
    except Exception as e:
        print(e)
        return
    with CsvWriter.CsvWriter('data') as datawriter:
        with Cgroup.CgroupCollector(datawriter, [os.path.join('docker',container['Id'])], key_prefixer=lambda cgpath, name : "/".join([name, image])) as cgmon:
            client.start(container=container['Id'])
            time.sleep(duration)
            client.stop(container=container['Id'])
    client.remove_container(container=container['Id'])
    global document
    document = { 'files' : ['data'] }

with docker.Client() as client:
    do(client)
