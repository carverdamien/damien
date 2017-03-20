import docker, time, threading, os, StringIO, csv, tarfile, tempfile, parse, platform, subprocess

assert(config != None)
assert(db != None)
assert(run != None)

kernel = config['kernel']
containers = config['containers']
root_mem_cgroup = subprocess.check_output(['lssubsys', '-m', 'memory'])[:-1].split(' ')[1]
mem_cgroup = {
    "docker" : {
        "memory" : {
            "use_hierarchy" : "1",
            "limit_in_bytes" : 2**30
        }
    }
}
if 'mem_cgroup' in config:
    mem_cgroup = config['mem_cgroup']
ALL_CTL = ['filebench_ctl', 'anon_ctl', 'boot_ctl', 'sysbench_ctl', 'cassandra_ctl', 'memtier_ctl']
for ctl in ALL_CTL:
    if ctl in config:
        globals()[ctl] = config[ctl]
    else:
        globals()[ctl] = []

class Filebench(threading.Thread):
    def __init__(self, container, duration, profile, pause_delay=None, pause_duration=None, start_delay=0, eventgen=1000, sleep=10, **kwargs):
        super(Filebench, self).__init__()
        container = docker.Client().inspect_container(container)
        while not container['State']['Running']:
            print('Starting %s' % (container))
            docker.Client().start(container)
            container = docker.Client().inspect_container(container)
        self.container = container
        self.start_delay = start_delay
        self.duration = duration
        self.pause_duration = pause_duration
        self.pause_delay = pause_delay
        self.profile = profile
        self.eventgen = eventgen
        self.sleep = sleep
        self.create_profile()
        self.create_fileset()
    def create_profile(self):
        path = '/usr/local/share/filebench/workloads/'
        with tempfile.TemporaryFile() as fileobj:
            with tarfile.open(mode='w', fileobj=fileobj) as tar:
                tarinfo = tarfile.TarInfo(self.profile['name']+'.f')
                tarinfo.size = len(self.profile['value'])
                tar.addfile(tarinfo, StringIO.StringIO(self.profile['value']))
            fileobj.seek(0)
            data = fileobj.read()
            docker.Client().put_archive(container=self.container, path=path, data=data)
    def create_fileset(self):
        frozencmd = "CG=/sys/fs/cgroup/freezer/%s && mkdir $CG && echo $$ > $CG/tasks" % (self.profile['name'])
        fbcmd = "load %s\n create files\n" % (self.profile['name'])
        bashcmd = "%s && echo '%s' | filebench" % (frozencmd, fbcmd)
        cmd = ['bash', '-c', bashcmd]
        print(cmd)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        pass
    def run(self):
        time.sleep(self.start_delay)
        fbcmd = ["load %s" % (self.profile['name']), "create files", "create processes", "eventgen rate = %d" % self.eventgen]
        fbcmd += ["stats clear", "sleep %d" % (self.sleep), "stats snap", 'stats dump "statsdump-%s.csv"' % (self.profile['name'])] * (self.duration/self.sleep)
        fbcmd += ["shutdown processes", "quit"]
        fbcmd = "\n".join(fbcmd)
        cmd = ['bash', '-c', "echo $$ >> /sys/fs/cgroup/freezer/%s/tasks && echo -e '%s' | filebench" % (self.profile['name'],fbcmd)]
        print(cmd)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        if self.pause_delay:
            def target():
                pausecmd = "echo FROZEN > /sys/fs/cgroup/freezer/%s/freezer.state" % (self.profile['name'])
                unpausecmd = "echo THAWED > /sys/fs/cgroup/freezer/%s/freezer.state" % (self.profile['name'])
                time.sleep(self.pause_delay)
                dockerexec = docker.Client().exec_create(container=self.container, cmd=['bash', '-c', pausecmd])
                for line in docker.Client().exec_start(dockerexec, stream=True):
                    print(line)
                time.sleep(self.pause_duration)
                dockerexec = docker.Client().exec_create(container=self.container, cmd=['bash', '-c', unpausecmd])
                for line in docker.Client().exec_start(dockerexec, stream=True):
                    print(line)
            t = threading.Thread(target=target)
            t.daemon = True
            t.start()
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=['cat','statsdump-%s.csv' % (self.profile['name'])])
        f = StringIO.StringIO(docker.Client().exec_start(dockerexec))
        csvreader = csv.reader(f)
        header = next(csvreader)
        for row in csvreader:
            data = { header[i]:row[i] for i in range(len(header))}
            data['Id'] = self.container['Id']
            data['profile'] = self.profile['name']
            db.filebench.insert_one(data)

class Anon(threading.Thread):
    def __init__(self, container, memory_in_bytes, duration=0, start_delay=0, **kwarg):
        super(Anon, self).__init__()
        container = docker.Client().inspect_container(container)
        while not container['State']['Running']:
            print('Starting %s' % (container))
            docker.Client().start(container)
            container = docker.Client().inspect_container(container)
        self.container = container
        self.start_delay = start_delay
        self.duration = duration
        self.memory_in_bytes = memory_in_bytes

    def run(self):
        time.sleep(self.start_delay)
        cmd = ['./anon', str(self.memory_in_bytes), str(self.duration)]
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        pass

class Boot(threading.Thread):
    def __init__(self, container, start_delay, duration, **kwargs):
        super(Boot, self).__init__()
        self.container = container
        self.start_delay = start_delay
        self.duration = duration
    def run(self):
        time.sleep(self.start_delay)
        docker.Client().start(self.container)
        time.sleep(self.duration)
        docker.Client().stop(self.container)

memtier_expected_output  = """[RUN{}]{:s}{threads} threads:{:s}{ops} ops,{:s}{ops_s} (avg:{:s}{avg_ops_s}) ops/sec,{:s}{mem_s}/sec (avg:{:s}{avg_mem_s}/sec),{:s}{ms_s} (avg:{:s}{avg_ms_s}) msec latency"""
memtier_parser = parse.compile(memtier_expected_output)
class Memtier(threading.Thread):
    def __init__(self, client_container, server_container, schedule, args=[], **kwargs):
        super(Memtier, self).__init__()
        client_container = docker.Client().inspect_container(client_container)
        while not client_container['State']['Running']:
            print('Starting %s' % (client_container))
            docker.Client().start(client_container)
            client_container = docker.Client().inspect_container(client_container)
        self.client_container = client_container
        server_container = docker.Client().inspect_container(server_container)
        while not server_container['State']['Running']:
            print('Starting %s' % (server_container))
            docker.Client().start(server_container)
            server_container = docker.Client().inspect_container(server_container)
        self.server_container = server_container
        self.schedule = schedule
        self.host = server_container['NetworkSettings']['IPAddress']
        self.port = '11211'
        self.protocol = 'memcache_text'
        self.datasize = 2**19
        self.nbc = 1
        self.nbt = 1
        self.args = args

    def run(self):
        for delay, duration in self.schedule:
            time.sleep(delay)
            cmd = [ 'memtier_benchmark',
                    '-s', self.host,
                    '-p', self.port,
                    '-P', self.protocol,
                    '-d', self.datasize,
                    '--test-time=%d' % duration,
                    '-c', self.nbc,
                    '-t', self.nbt ] + self.args
            dockerexec = docker.Client().exec_create(container=self.client_container['Id'], cmd=[str(c) for c in cmd])
            for line in docker.Client().exec_start(dockerexec, stream=True):
                timestamp = time.time()
                res = memtier_parser.search(line)
                if res != None:
                    res.named['Id'] = self.client_container['Id']
                    res.named['timestamp'] = timestamp
                    db.memtier.insert_one(res.named)
                elif line not in ['','\n']:
                    print(line[:-1])

cassandra_expected_output = """total,{:s}{total_ops},{:s}{op_s},{:s}{pk_s},{:s}{row_ps},{:s}{mean},{:s}{med},{:s}{perc95},{:s}{perc99},{:s}{perc999},{:s}{max},{:s}{time},{:s}{stderr},{:s}{erros},{:s}{gc_count},{:s}{max_ms},{:s}{sum_ms},{:s}{sdv_ms},{:s}{mb}"""
cassandra_parser = parse.compile(cassandra_expected_output)
class Cassandra(threading.Thread):
    def __init__(self, container, schedule, writes, threads, **kwargs):
        super(Cassandra, self).__init__()
        container = docker.Client().inspect_container(container)
        while not container['State']['Running']:
            print('Starting %s' % (container))
            docker.Client().start(container)
            container = docker.Client().inspect_container(container)
        self.container = container
        self.schedule = schedule
        self.threads = threads
        time.sleep(60)
        cmd = ['write', 'n=%s' % writes]
        self.cassandra(cmd)
    def cassandra(self, cmd):
        cmd = ['cassandra-stress'] + cmd
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            timestamp = time.time()
            res = cassandra_parser.search(line)
            if res != None:
                res.named['Id'] = self.container['Id']
                res.named['timestamp'] = timestamp
                db.cassandra.insert_one(res.named)
            elif line not in ['','\n']:
                print(line[:-1])
    def run(self):
        for delay, duration in self.schedule:
            time.sleep(delay)
            cmd = ['read', 'duration=%s' % duration, '-rate', 'threads=%s' % self.threads]
            self.cassandra(cmd)

sysbench_bin_path = './sysbench/sysbench'
sysbench_lua_path = './sysbench/tests/db/oltp.lua'
sysbench_expected_v05_intermediate_output = """[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
sysbench_parser = parse.compile(sysbench_expected_v05_intermediate_output)
class Sysbench(threading.Thread):
    def __init__(self, client_container, server_container, dbsize, oltp_read_only, threads, schedule, dbname='sysbench', **kwargs):
        super(Sysbench, self).__init__()
        client_container = docker.Client().inspect_container(client_container)
        while not client_container['State']['Running']:
            print('Starting %s' % (client_container))
            docker.Client().start(client_container)
            client_container = docker.Client().inspect_container(client_container)
        self.client_container = client_container
        server_container = docker.Client().inspect_container(server_container)
        while not server_container['State']['Running']:
            print('Starting %s' % (server_container))
            docker.Client().start(server_container)
            server_container = docker.Client().inspect_container(server_container)
        self.server_container = server_container
        self.host = self.server_container['NetworkSettings']['IPAddress']
        self.schedule = schedule
        self.oltp_read_only = oltp_read_only
        self.threads = threads
        self.dbsize = dbsize
        self.dbname = dbname
        self.wait_for_server_to_start()
        if self.create_db():
            self.fill_db()
    def mysql(self, cmd):
        cmd = ['mysql', '--host', '127.0.0.1', '-u', 'root'] + cmd
        return docker.Client().exec_create(container=self.server_container, cmd=cmd)
    def wait_for_server_to_start(self):
        while True:
            try:
                dockerexec = self.mysql(['-e', 'show status']) 
                for line in docker.Client().exec_start(dockerexec, stream=True):
                    print(line)
                inspect = docker.Client().exec_inspect(dockerexec)
                if inspect['ExitCode'] == 0:
                    print('mysqld started!')
                    break
            except Exception as e:
                print(e)
            print('Waiting for %s to start' % self.server_container)
            time.sleep(10)
    def create_db(self):
        dockerexec = self.mysql(['-e', 'CREATE DATABASE %s' % self.dbname])
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        inspect = docker.Client().exec_inspect(dockerexec)
        return inspect['ExitCode'] == 0
    def sysbench(self, cmd):
        cmd = [sysbench_bin_path, '--test=%s' % sysbench_lua_path, '--oltp-table-size=%d' % self.dbsize, '--mysql-db=%s' % self.dbname, '--mysql-host=%s' % self.host, '--mysql-user=root', '--mysql-password='] + cmd
        return docker.Client().exec_create(container=self.client_container, cmd=cmd)
    def fill_db(self):
        dockerexec = self.sysbench(['prepare'])
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
    def run(self):
        for delay, duration in self.schedule:
            time.sleep(delay)
            cmd = ['--report-interval=1',
                   '--max-requests=0',
                   '--max-time=%d' % duration,
                   '--num-threads=%d' % self.threads, 'run']
            if self.oltp_read_only:
                cmd = ['--oltp-read-only=on'] + cmd
            dockerexec = self.sysbench(cmd)
            for line in docker.Client().exec_start(dockerexec, stream=True):
                res = sysbench_parser.search(line)
                if res != None:
                    res.named['Id'] = self.client_container['Id']
                    db.sysbench.insert_one(res.named)
                elif line not in ['','\n']:
                    print(line[:-1])
### MAIN ###
if not platform.release() == kernel:
    environ = os.environ.copy()
    environ['PATH'] = "%s:./submodules/grub-list" % environ['PATH']
    subprocess.check_call(['./submodules/grub-list/grub-reboot-on', kernel], env=environ)
    raise
client = docker.Client()        

assert len([c for c in client.containers(all=True)]) == 0, "docker rm -fv $(docker ps -aq)"

def recrmdir(path):
    for p in os.listdir(path):
        p = os.path.join(path,p)
        if os.path.isdir(p):
            recrmdir(p)
    os.rmdir(path)

def create_mem_cgroup(path, memory={}, children={}):
    print('Creating %s' % path)
    if os.path.isdir(path):
        recrmdir(path)
    os.mkdir(path)
    for m in memory:
        value = int(memory[m])
        p = os.path.join(path,"memory.%s" % m)
        print('Setting %s as %s' % (p,value))
        with open(p,'w') as f:
            f.write("%d\n" % value)
        with open(p) as f:
            assert (value == int(f.read())), 'Could not set %s as %s' % (p,value)
    for c in children:
        v = children[c]
        p = os.path.join(path,c)
        create_mem_cgroup(p, **v)

def destroy_mem_cgroup(path, memory={}, children={}):
    if os.path.isdir(path):
        for c in children:
            v = children[c]
            p = os.path.join(path,c)
            destroy_mem_cgroup(c, **v)
        recrmdir(path)

for k in mem_cgroup:
    create_mem_cgroup(os.path.join(root_mem_cgroup, k), **mem_cgroup[k])

def create_container(containers):
    if type(containers) != list:
        containers = [containers]
    for container in containers:
        if 'host_config' in  container:
                container['host_config'] = client.create_host_config(
                    **container['host_config'])
        client.pull(container['image'])
        yield client.create_container(**container)
containers = [c for c in create_container(containers)]
ctl = []
ctl += [Filebench(**conf) for conf in filebench_ctl]
ctl += [Anon(**conf) for conf in anon_ctl]
ctl += [Boot(**conf) for conf in boot_ctl]
ctl += [Sysbench(**conf) for conf in sysbench_ctl]
ctl += [Cassandra(**conf) for conf in cassandra_ctl]
ctl += [Memtier(**conf) for conf in memtier_ctl]
try:
    with open('/proc/sys/vm/drop_caches', 'w') as f:
        f.write("3\n")
except Exception as e:
    print(e)
for c in ctl: c.start()
for c in ctl: c.join()
for c in containers:
    client.stop(c)
    client.remove_container(c, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'containers': containers }})
for k in mem_cgroup:
    destroy_mem_cgroup(os.path.join(root_mem_cgroup, k), **mem_cgroup[k])
