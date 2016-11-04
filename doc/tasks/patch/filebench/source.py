import docker, time, threading, os, StringIO, csv, tarfile, tempfile, parse, platform, subprocess
# from submodules.filebench.Filebench import Filebench # TODO: move class Filebench here

assert(config != None)
assert(db != None)
assert(run != None)

kernel = config['kernel']
total_mem_limit = config['total_mem_limit']
containers = config['containers']
filebench_ctl = []
if 'filebench_ctl' in config:
    filebench_ctl = config['filebench_ctl']
anon_ctl = []
if 'anon_ctl' in config:
    anon_ctl = config['anon_ctl']
boot_ctl = []
if 'boot_ctl' in config:
    boot_ctl = config['boot_ctl']
sysbench_ctl = []
if 'sysbench_ctl' in config:
    sysbench_ctl = config['sysbench_ctl']

class Filebench(threading.Thread):
    def __init__(self, container, duration, profile, pause_delay=None, pause_duration=None, start_delay=0, eventgen=1000, **kwargs):
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
        fbcmd += ["stats clear", "sleep 10", "stats snap", 'stats dump "statsdump-%s.csv"' % (self.profile['name'])] * (self.duration/10)
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

sysbench_bin_path = './sysbench/sysbench'
sysbench_lua_path = './sysbench/tests/db/oltp.lua'
sysbench_expected_v05_intermediate_output = """[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}"""
sysbench_parser = parse.compile(sysbench_expected_v05_intermediate_output)
class Sysbench(threading.Thread):
    def __init__(self, client_container, server_container, dbsize, oltp_read_only, threads, schedule, dbname='sysbench'):
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

if not platform.release() == kernel:
    environ = os.environ.copy()
    environ['PATH'] = "%s:./submodules/grub-list" % environ['PATH']
    subprocess.check_call(['./submodules/grub-list/grub-reboot-on', kernel], env=environ)
    raise
client = docker.Client()        
assert(len([c for c in client.containers(all=True)]) == 0)
try:
    if os.path.exists('/sys/fs/cgroup/memory/docker'):
        os.rmdir('/sys/fs/cgroup/memory/docker')
    os.mkdir('/sys/fs/cgroup/memory/docker')
    with open('/sys/fs/cgroup/memory/docker/memory.limit_in_bytes', 'w') as f:
        f.write("%d\n" % total_mem_limit)
    with open('/sys/fs/cgroup/memory/docker/memory.use_hierarchy', 'w') as f:
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
                    **container['host_config'])
        client.pull(container['image'])
        yield client.create_container(**container)
containers = [c for c in create_container(containers)]
clt = [Filebench(**conf) for conf in filebench_ctl] + [Anon(**conf) for conf in anon_ctl] + [Boot(**conf) for conf in boot_ctl] + [Sysbench(**conf) for conf in sysbench_ctl]
try:
    with open('/proc/sys/vm/drop_caches', 'w') as f:
        f.write("3\n")
except Exception as e:
    print(e)
for c in clt: c.start()
for c in clt: c.join()
for c in containers:
    client.stop(c)
    client.remove_container(c, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'containers': containers }})
