import Collector
import subprocess, time, os, tempfile

class Cgroup(object):
    def __init__(self, name, path, **kwargs):
        self.name = name
        self.path = path
        self.kwargs = kwargs
        self.config = cg_config(self.path, **kwargs)

    def Popen(self, call, **kwargs):
        return subprocess.Popen(['cgexec', '-g', 'memory:'+self.path, '-g', 'cpuacct:'+self.path, '-g', 'cpuset:'+self.path] + call, **kwargs)

    def check_call(self, call, **kwargs):
        subprocess.check_call(['cgexec', '-g', 'memory:'+self.path, '-g', 'cpuacct:'+self.path, '-g', 'cpuset:'+self.path] + call, **kwargs)

def create(cgroups):
    config = "\n".join([c.config for c in sorted(cgroups, key=lambda c: len(c.path.split('/')))])
    cg_create(config)

def get_subsys_mount_point(subsys):
    p = subprocess.Popen(['lssubsys', '-m', subsys], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for l in out.split(str.encode('\n')):
        l = l.decode('utf-8')
        if len(l):
            mount_point = l.split(' ')[1]
    return mount_point + '/'

class CgroupCollector(Collector.Collector):
    def __init__(self, data_writer, paths, sleep_delay=1):
        super(CgroupCollector, self).__init__(data_writer, sleep_delay)
        paths = list(set(paths))
        print('Monitoring:'+str(paths))
        self.paths = paths
        self.last = {}

    def collect_function(self):
        memory_mount_point = get_subsys_mount_point('memory')
        cpuacct_mount_point = get_subsys_mount_point('cpuacct')
        SC_CLK_TCK = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        values = []
        for cgpath in self.paths:
            last = {}
            if cgpath in self.last:
                last = self.last[cgpath]
            v = { 'timestamp' : time.time() }
            # MEMORY
            directory = os.path.normpath(memory_mount_point + cgpath)
            for name in ['usage_in_bytes', 'limit_in_bytes', 'max_usage_in_bytes', 'soft_limit_in_bytes', 'failcnt'] + ['memsw.usage_in_bytes', 'memsw.limit_in_bytes', 'memsw.max_usage_in_bytes', 'memsw.failcnt']:
                path = os.path.join(directory, 'memory.'+name)
                with open(path) as f:
                    key = "/".join([cgpath, name])
                    v[key] = int(f.readline())
                path = os.path.join(directory, 'memory.stat')
                with open(path) as f:
                    for l in f:
                        name, val = l.split(' ')
                        val = int(val)
                        key = "/".join([cgpath, name]) 
                        v[key] = val
            # CPUACCT
            newglobalcpu = 0
            global_cpu = "/".join([cgpath, "global_cpu"])
            if global_cpu in last:
                lastglobalcpu = last[global_cpu]
            newglobalcpus = {}
            lastglobalcpus = {}
            global_cpus = "/".join([cgpath, "global_cpus"])
            if global_cpus in last:
                lastglobalcpus = last[global_cpus]
            last[global_cpus] = {}
            with open('/proc/stat') as f:
                for e in f.readline().split(' '):
                    try:
                        newglobalcpu += int(e)
                    except:
                        pass
                newglobalcpu *= 1e9 / SC_CLK_TCK
                v[global_cpu] = newglobalcpu
                last[global_cpu] = v[global_cpu]
                while True:
                    split = f.readline().split(' ')
                    if split[0][0:3] != "cpu":
                        break
                    cpuid = int(split[0][3:])
                    new = 0
                    for e in split[1:]:
                        try:
                            new += int(e)
                        except:
                            pass
                    new *= 1e9 / SC_CLK_TCK
                    newglobalcpus[cpuid] = new
                    last[global_cpus][cpuid] = new
            directory = os.path.normpath(cpuacct_mount_point + cgpath)
            path = os.path.join(directory, 'cpuacct.usage_percpu')
            with open(path) as f:
                cpus = f.readline().split(' ')[:-1] # Skip \n
                ncpus = len(cpus)
                for i in range(ncpus):
                    cpu = "/".join([cgpath, "cpu-%d" % (i)])
                    newcpu = int(cpus[i]) # TODO: percentage
                    v[cpu] = newcpu
                    pcpu = "/".join([cgpath, "cpu-%d%%" % (i)])
                    v[pcpu] = ''
                    if cpu in last:
                        lastcpu = last[cpu]
                        deltacpu = newcpu - lastcpu
                        deltaglobalcpu = newglobalcpus[i] - lastglobalcpus[i]
                        if deltaglobalcpu != 0:
                            v[pcpu] = 100.0 * deltacpu / deltaglobalcpu
                    last[cpu] = v[cpu]
            path = os.path.join(directory, 'cpuacct.usage')
            with open(path) as f:
                newcpu = int(f.readline()) # TODO: percentage
                cpu = "/".join([cgpath, "cpu"])
                pcpu = "/".join([cgpath, "cpu%"])
                v[cpu] = newcpu
                v[pcpu] = ''
                if cpu in last:
                    lastcpu = last[cpu]
                    deltacpu = newcpu - lastcpu
                    deltaglobalcpu = newglobalcpu - lastglobalcpu
                    if deltaglobalcpu != 0:
                        v[pcpu] = 100.0 * ncpus * deltacpu / deltaglobalcpu
                last[cpu] = v[cpu]
            self.last[cgpath] = last
            values.append(v)
        return values

# TODO : Add BLKIO, ...

def cg_create(conf):
    f = tempfile.NamedTemporaryFile()
    f.write(conf.encode('utf-8'))
    f.flush()
    subprocess.check_call(['sudo', 'cgconfigparser', '-l', f.name, '-f', '777', '-d', '777', '-s', '777'])
    f.close()

def cg_config_cpuacct(cpuacct):
    return ['cpuacct {}']

def cg_config_cpuset(cpuset):
    return ["cpuset {",
            'cpuset.cpus = "%s";' % cpuset['cpus'], # Required
            'cpuset.mems = "%s";' % cpuset['mems'], # Required
            '}']

def cg_config_memory(memory):
    res = ['memory {']
    for key in memory.keys():
        res += ['memory.%s = "%d";' % (key, memory[key])] # Optinals
    res += ['}']
    return res
 
def cg_config(cgpath, cpuacct=None, cpuset=None, memory=None):
    res = ['group %s {' % cgpath]
    if cpuacct != None:
        res += cg_config_cpuacct(cpuacct)
    if cpuset != None:
        res += cg_config_cpuset(cpuset)
    if memory != None:
        res += cg_config_memory(memory)
    res += ['}']
    return "\n".join(res)

def cg_delete(cgpath):
    i = 0
    while True:
        i+=1
        if i > 10:
            raise Exception('Cannot cgdelete %s' % cgpath)
        subprocess.Popen(['sudo', 'cgdelete','-r','-g','memory:'+cgpath, '-g','cpuacct:'+cgpath, '-g','cpuset:'+cgpath],
                         stdout=open('/dev/null','w'), stderr=open('/dev/null','w')).wait()
        p = subprocess.Popen(['lscgroup', '-g', 'memory:'+cgpath, '-g','cpuacct:'+cgpath, '-g','cpuset:'+cgpath])
        p.wait()
        if not p.returncode:
            break

def _cg_Popen(cgpath, args, **kwargs):
    return subprocess.Popen(['cgexec', '-g', 'memory:'+cgpath, '-g', 'cpuacct:'+self.path, '-g', 'cpuset:'+self.path] + args, **kwargs)

def cg_Popen(cgpath):
    return lambda args, **kwargs : _cg_Popen(cgpath, args, **kwargs)

def my_cgpath():
    cgpaths = set()
    with open('/proc/self/cgroup') as f:
        for line in f:
            line = line[:-1] # rm \n
            [_,subsys,cgpath] = line.split(':')
            if subsys in ['cpuacct', 'memory']:
                cgpaths.add(cgpath)
    if len(cgpaths) != 1:
        raise Exception('len(cgpaths) != 1')
    for cgpath in cgpaths:
        return cgpath
