#!/usr/bin/env python
import docker, time, subprocess, parse, datetime, os
import lib.CsvWriter as CsvWriter
import lib.Cgroup as Cgroup

N = 3
dbsize = 15000000
image = 'mysql:latest'
mem_limit = 3 * 2**30
sysbench_bin_path = './submodules/sysbench/sysbench/sysbench'
sysbench_lua_path = './submodules/sysbench/sysbench/tests/db/oltp.lua'
expected_v05_intermediate_output = \
"""[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
parser = parse.compile(expected_v05_intermediate_output)
environment = {'MYSQL_ALLOW_EMPTY_PASSWORD' : 'yes'}

class Sysbench(object):
    def __init__(self, prefix, host, dbsize):
        self.prefix = prefix
        self.host = host
        self.dbsize = dbsize
    def mysql(self, call, **kwargs):
        call = ['mysql', '--host', self.host, '-u', 'root'] + call
        return subprocess.Popen(call, **kwargs)
    def wait_for_server_to_start(self):
        while True:
            p = self.mysql([], stdin=open('/dev/null'))
            p.wait()
            if p.returncode == 0:
                print('mysqld started!')
                break
            else:
                print('Waiting for %s to start' % self.host)
                time.sleep(10)
    def create_db(self):
        p = self.mysql(['-e', 'CREATE DATABASE sysbench'])
        p.wait()
        if p.returncode != 0:
            raise Exception()
    def sysbench(self, call, **kwargs):
        call = [sysbench_bin_path, '--test=%s' % sysbench_lua_path, '--oltp-table-size=%d' % self.dbsize, '--mysql-db=sysbench', '--mysql-host=%s' % self.host, '--mysql-user=root', '--mysql-password='] + call
        return subprocess.Popen(call, **kwargs)
    def fill_db(self):
        p = self.sysbench(['prepare'])
        p.wait()
        if p.returncode != 0:
            raise Exception()
    def bench(self, perfwriter, threads, duration):
        p = self.sysbench(['--report-interval=1',
                           '--max-time=%d' % duration, 
                           '--num-threads=%d' % threads, 'run'], stdout=subprocess.PIPE)
        for line in p.stdout:
            res = parser.search(line)
            if res != None:
                timestamp = datetime.datetime.fromtimestamp(int(res.named['timestamp']))
                for k,v in res.named.iteritems():
                    if k == 'timestamp':
                        continue
                    label = "/".join([self.prefix, k])
                    perfwriter.write(x=timestamp,y=v,label=label)
            elif line not in ['','\n']:
                print(line[:-1])
        p.wait()
        if p.returncode != 0:
            raise Exception()

def getIp(client, container):
    inspect = client.inspect_container(container)
    return inspect['NetworkSettings']['IPAddress']

def main(client):
    for line in client.pull(image, stream=True):
        print(line)
    host_config = client.create_host_config(mem_limit=mem_limit, oom_kill_disable=True)
    container = [client.create_container(image=image,
                                         host_config=host_config,
                                        environment=environment) for i in range(N)]
    mapping = { os.path.join('docker',container[i]['Id']) : "mysql%d" % i for i in range(N)}
    mapping['docker'] = 'docker'
    cgpaths = mapping.keys()
    key_prefixer = lambda cgpath, name : "/".join([mapping[cgpath],name])
    with CsvWriter.CsvWriter('perf') as perfwriter, CsvWriter.CsvWriter('memory') as memorywriter:
        with Cgroup.CgroupCollector(memorywriter,
                                    cgpaths,
                                    key_prefixer=key_prefixer) as cgmon:
            for i in range(N):
                client.start(container[i])
            sysbench = [Sysbench('mysql%d' % i, getIp(client, container[i]), dbsize) for i in range(N)]
            for i in range(N):
                sysbench[i].wait_for_server_to_start()
                sysbench[i].create_db()
                sysbench[i].fill_db()
            for i in range(N):
                sysbench[i].bench(perfwriter=perfwriter, threads=8, duration=30*60)
            for i in range(N):
                client.stop(container[i])
                client.remove_container(container[i])
    global document
    document = { 'files' : ['memory', 'perf'] }

with docker.Client() as client:
    main(client)
