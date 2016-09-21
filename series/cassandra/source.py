#!/usr/bin/env python
import json, os, time
import lib.CsvWriter as CsvWriter
import lib.Cgroup as Cgroup
import docker, parse, datetime

N = 1 # 4
image = 'cassandra:latest'
mem_limit = 3*2**30
start_wait = 3*60
#cmd = ['cassandra-stress', 'mixed', 'ratio(write=1,read=3)', 'n=100000', '-rate', 'threads=4']]
cmd = ['cassandra-stress', 'write', 'duration=3m', '-rate', 'threads=4']
                # """type totalops,op/s,pk/s,row/s,mean,med,.95,.99,.999,max,time,stderr,errors,gc: #,max ms, sum ms,sdv ms,mb"""
expected_output = """total,{:s}{total_ops},{:s}{op_s},{:s}{pk_s},{:s}{row_ps},{:s}{mean},{:s}{med},{:s}{perc95},{:s}{perc99},{:s}{perc999},{:s}{max},{:s}{time},{:s}{stderr},{:s}{erros},{:s}{gc_count},{:s}{max_ms},{:s}{sum_ms},{:s}{sdv_ms},{:s}{mb}"""
parser = parse.compile(expected_output)

def do(client):
    # todo: docker ps -aq | xargs docker rm -f
    # todo: limit docker to 6G
    try:
        for line in client.pull(image, stream=True):
            print(line)
        host_config = client.create_host_config(mem_limit=mem_limit)
        container = [client.create_container(image=image,host_config=host_config) for i in range(N)]
        mapping = { os.path.join('docker',container[i]['Id']) : "c%d" % i for i in range(N)}
        mapping['docker'] = 'docker'
        cgpaths = mapping.keys()
        key_prefixer = lambda cgpath, name : "/".join([mapping[cgpath],name])
    except Exception as e:
        print(e)
        return
    with CsvWriter.CsvWriter('memory') as memorywriter, CsvWriter.CsvWriter('perf') as perfwriter:
        with Cgroup.CgroupCollector(memorywriter, cgpaths, key_prefixer=key_prefixer) as cgmon:
            for i in range(N):
                client.start(container=container[i]['Id'])
                time.sleep(start_wait)
            for i in range(N):
                run = client.exec_create(container=container[i], cmd=cmd)
                for line in client.exec_start(exec_id=run['Id'], stream=True):
                    timestamp = datetime.datetime.fromtimestamp(time.time())
                    res = parser.search(line)
                    if res != None:
                        for k,v in res.named.iteritems():
                            perfwriter.write(x=timestamp,y=v,label=k)
                    else:
                        print(line)
            for i in range(N):
                client.stop(container=container[i]['Id'])
    for i in range(N):
        client.remove_container(container=container[i]['Id'])
    global document
    document = { 'files' : ['memory', 'perf'] }

with docker.Client() as client:
    do(client)
