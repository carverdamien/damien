import docker, time, subprocess, parse, threading, os, StringIO, csv
# from submodules.filebench.Filebench import Filebench # TODO: move class Filebench here

assert(config != None)
assert(db != None)
assert(run != None)

total_mem_limit = config['total_mem_limit']
containers = config['containers']
filebench_ctl = config['filebench_ctl']
"""   25: 11.435: 1476286201,IO Summary,357052,35702.493751,178.786448,,,11515.627115,1156.012374,190.331897"""
exepected_output = """   {:S}: {:S}: {timestamp},{flowop},{ops},{opsPs},{mbPs},{msPsop},{usPop-cpu},{r},{w},{uscpuPop}\n"""
parser = parse.compile(exepected_output)

class Filebench(threading.Thread):
    def __init__(self, container, duration, start_delay=0, **kwargs):
        super(Filebench, self).__init__()
        docker.Client().start(container)
        self.container = docker.Client().inspect_container(container)
        self.start_delay = start_delay
        self.duration = duration
        self.create_profile()
        self.create_fileset()
    def create_profile(self):
        path = '/usr/local/share/filebench/workloads/'
        with open('./series/filebench/profile.tar') as f:
            data = f.read()
            docker.Client().put_archive(container=self.container, path=path, data=data)
    def create_fileset(self):
        fbcmd = "load profile\n create fileset\n"
        cmd = ['bash', '-c', 'echo \'%s\' | filebench' % fbcmd]
        print(cmd)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        pass
    def run(self):
        time.sleep(self.start_delay)
        fbcmd = ["load profile", "create fileset", "create processes"]
        fbcmd += ["stats clear", "sleep 10", "stats snap", 'stats dump "statsdump.csv"'] * (self.duration/10)
        fbcmd += ["shutdown processes", "quit"]
        fbcmd = "\n".join(fbcmd)
        cmd = ['bash', '-c', "echo -e '%s' | filebench" % fbcmd]
        print(cmd)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=cmd)
        for line in docker.Client().exec_start(dockerexec, stream=True):
            print(line)
        dockerexec = docker.Client().exec_create(container=self.container, cmd=['cat','statsdump.csv'])
        f = StringIO.StringIO(docker.Client().exec_start(dockerexec))
        csvreader = csv.reader(f)
        header = next(csvreader)
        for row in csvreader:
            data = { header[i]:row[i] for i in range(len(header))}
            print(data)

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
clt = [Filebench(**conf) for conf in filebench_ctl]
for c in clt: c.start()
for c in clt: c.join()
for c in containers:
    client.stop(c)
    client.remove_container(c, v=True)
db.run.update_one({'_id':run['_id']}, {'$set':{ 'containers': containers }})
