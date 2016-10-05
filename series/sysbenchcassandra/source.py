import docker, time, subprocess, parse, threading, os

assert(config != None)
assert(db != None)
assert(run != None)

total_mem_limit = config['total_mem_limit']
docker_containers = config['docker_containers']
sysbench_ctl = config['sysbench_ctl']
cassandra_clt = config['cassandra_clt']

sysbench_bin_path = './submodules/sysbench/sysbench/sysbench'
sysbench_lua_path = './submodules/sysbench/sysbench/tests/db/oltp.lua'
expected_v05_intermediate_output = \
"""[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
parser = parse.compile(expected_v05_intermediate_output)

class Sysbench(threading.Thread):
    def __init__(self, container, duration, dbsize, oltp_read_only, threads):
        super(Sysbench, self).__init__()
        self.container = docker.Client().inspect_container(container)
        self.host = self.container['NetworkSettings']['IPAddress']
        self.duration = duration
        self.oltp_read_only = oltp_read_only
        self.threads = threads
        self.dbsize = dbsize
        self.wait_for_server_to_start()
        self.create_db()
        self.fill_db()
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
    def run(self):
        cmd = ['--report-interval=1',
               '--max-requests=0',
               '--max-time=%d' % self.duration,
               '--num-threads=%d' % self.threads, 'run']
        if self.oltp_read_only:
            cmd = ['--oltp-read-only=on'] + cmd
        p = self.sysbench(cmd, stdout=subprocess.PIPE)
        for line in p.stdout:
            res = parser.search(line)
            if res != None:
                res.named['Id'] = self.container['Id']
                db.sysbench.insert_one(res.named)
            elif line not in ['','\n']:
                print(line[:-1])
        p.wait()
        if p.returncode != 0:
            raise Exception()

class Cassandra(threading.Thread):
    def __init__(self, container, start, duration, **kwargs):
        super(Cassandra, self).__init__()
        self.container = container
        self.start = start
        self.duration = duration
    def run(self):
        time.sleep(self.start)
        docker.Client().start(self.container)
        time.sleep(self.duration)

client = docker.Client()        
assert(len([c for c in client.containers(all=True)]) == 0)
try:
    if os.path.isdir('/sys/fs/cgroup/memory/docker'):
        os.mkdir('/sys/fs/cgroup/memory/docker')
    with open('/sys/fs/cgroup/memory/docker/memory.limit_in_bytes', w) as f:
        f.write("%d\n" % total_mem_limit)
    with open('/sys/fs/cgroup/memory/docker/memory.use_hierarchy', w) as f:
        f.write("1\n")
except Exception as e:
    print(e)
with open('/sys/fs/cgroup/memory/docker/memory.limit_in_bytes') as f:
    assert(total_mem_limit == int(f.read()))
with open('/sys/fs/cgroup/memory/docker/memory.use_hierarchy') as f:
    assert(1 == int(f.read()))
def create_container(containers):
    if type(containers) != list:
        containers = [containers]
    for container in containers:
        if 'host_config' in  container:
                container['host_config'] = client.create_host_config(
                    container['host_config'])
        client.pull(container['image'])
        yield client.create_container(**container)
containers = [c for c in create_container(containers)]
clt = [Cassandra(**c) for c in cassandra_clt] + [Sysbench(**s) for s in sysbench_ctl]
for c in clt: c.start()
for c in clt: c.join()
for c in containers:
    client.stop(c)
    client.remove_container(c, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'containers': containers }})
