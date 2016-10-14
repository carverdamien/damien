import docker, time, subprocess, parse, threading, os, StringIO, csv, tarfile, tempfile
# from submodules.filebench.Filebench import Filebench # TODO: move class Filebench here

assert(config != None)
assert(db != None)
assert(run != None)

total_mem_limit = config['total_mem_limit']
containers = config['containers']
filebench_ctl = config['filebench_ctl']
anon_ctl = config['anon_ctl']
"""   25: 11.435: 1476286201,IO Summary,357052,35702.493751,178.786448,,,11515.627115,1156.012374,190.331897"""
exepected_output = """   {:S}: {:S}: {timestamp},{flowop},{ops},{opsPs},{mbPs},{msPsop},{usPop-cpu},{r},{w},{uscpuPop}\n"""
parser = parse.compile(exepected_output)

class Filebench(threading.Thread):
    def __init__(self, container, duration, profile, pause_delay=None, pause_duration=None, start_delay=0, **kwargs):
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
        fbcmd = "load %s\n create fileset\n" % (self.profile['name'])
        bashcmd = "%s && echo '%s' | filebench" % (frozencmd, fbcmd)
        cmd = ['bash', '-c', bashcmd]
        print(cmd)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        pass
    def run(self):
        time.sleep(self.start_delay)
        fbcmd = ["load %s" % (self.profile['name']), "create fileset", "create processes"]
        fbcmd += ["stats clear", "sleep 10", "stats snap", 'stats dump "statsdump.csv"'] * (self.duration/10)
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
        dockerexec = docker.Client().exec_create(container=self.container, cmd=['cat','statsdump.csv'])
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
clt = [Filebench(**conf) for conf in filebench_ctl] + [Anon(**conf) for conf in anon_ctl]
for c in clt: c.start()
for c in clt: c.join()
for c in containers:
    client.stop(c)
    client.remove_container(c, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'containers': containers }})
