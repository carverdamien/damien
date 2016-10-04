import docker, time, subprocess, parse

assert(config != None)
assert(db != None)
assert(run != None)

dbsize = config['dbsize']
oltp_read_only = config['oltp_read_only']
mem_limit = config['mem_limit']
cpuset_cpus = config['cpuset_cpus']
device_read_bps = config['device_read_bps']
device_write_bps = config['device_write_bps']
#cpuset_cpus ? cpu_group/cpu_period?
#device_read_bps/device_write_bps? device_read_iops/device_write_iops?
threads = config['threads']
duration = config['duration']

image = 'mysql:latest'
sysbench_bin_path = './submodules/sysbench/sysbench/sysbench'
sysbench_lua_path = './submodules/sysbench/sysbench/tests/db/oltp.lua'
expected_v05_intermediate_output = \
"""[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
parser = parse.compile(expected_v05_intermediate_output)
environment = {'MYSQL_ALLOW_EMPTY_PASSWORD' : 'yes'}

class Sysbench(object):
    def __init__(self, container, host, dbsize):
        self.container = container
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
    def bench(self, db, threads, duration, oltp_read_only):
        cmd = ['--report-interval=1',
               '--max-requests=0',
               '--max-time=%d' % duration,
               '--num-threads=%d' % threads, 'run']
        if oltp_read_only:
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

def getIp(client, container):
    inspect = client.inspect_container(container)
    return inspect['NetworkSettings']['IPAddress']

client = docker.Client()
assert(len([c for c in client.containers(all=True)]) == 0)
for line in client.pull(image, stream=True): print(line)
host_config = client.create_host_config(mem_limit=mem_limit, oom_kill_disable=True, cpuset_cpus=cpuset_cpus, device_write_bps=device_write_bps, device_read_bps=device_read_bps)
container = client.create_container(image=image, host_config=host_config, environment=environment)
client.start(container)
sysbench = Sysbench(container, getIp(client, container), dbsize)
sysbench.wait_for_server_to_start()
sysbench.create_db()
sysbench.fill_db()
sysbench.bench(db, threads=threads, duration=duration, oltp_read_only=oltp_read_only)
client.stop(container)
client.remove_container(container, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'container': container}})
