import threading, time, graphviz, datetime

class GThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None, taskname=None, cgroup=None, args=(), kwargs={}):
        super(GThread, self).__init__(group, target, name, args, kwargs)
        self.fathers = []
        self.sons = []
        self.start_time = None
        self.finish_time = None
        self.taskname = taskname
        self.cgroup = cgroup

    def run(self):
        for f in self.fathers:
            f.join()
        self.start_time = time.time()
        super(GThread, self).run()
        self.finish_time = time.time()

class Gantt(object):
    def __init__(self, tasks, graph):
        """
        tasks: dictionary of tasks object.
        tasks should be already created, initialized and ready to receive work orders.

        nodes: dictionary of nodes refering to tasks and work until mode

        edges: dictionary of edges (dependencies between nodes)
        
        The Graph must be a Tree.
        """
        self.tasks = tasks
        self.graph = graph
        nodes = graph['nodes']
        edges = graph['edges']
        self.threads = [GThread(taskname='Start')]
        for node in nodes[1:-1]:
            name = node['task']
            task = self.tasks[name]
            cgroup = str(task.cgroup.path)
            target = getattr(task, node['target'])
            args = tuple(node['args'])
            taskname = "%s.%s%s" % (name, node['target'], str(args))
            self.threads.append(GThread(taskname=taskname, target=target, args=args, cgroup=cgroup))
        self.threads.append(GThread(taskname='Finish'))
        for e in edges:
            father = self.threads[e[0]]
            son = self.threads[e[1]]
            son.fathers.append(father)
            father.sons.append(son)
        for thread in self.threads[1:]:
            if len(thread.fathers) == 0:
                raise Exception('len(thread.fathers) == 0')
    
    def start(self):
        t = self.threads[0]
        to_start = set(self.threads)
        t.start()
        to_start.remove(t)
        while len(to_start) != 0:
            for t in to_start:
                f_in_to_start = False
                for f in t.fathers:
                    if f in to_start:
                        f_in_to_start = True
                        break
                if not f_in_to_start:
                    break
            t.start()
            to_start.remove(t)

    def join(self):
        for t in self.threads:
            t.join()

    def report(self):
        tasksname = [t.taskname for t in self.threads]
        seen = set()
        seen_add = seen.add
        tasksname = [x for x in tasksname if not (x in seen or seen_add(x))] # rm duplicates and keeps order
        taskY = { t:tasksname.index(t) for t in tasksname}
        for t in  self.threads:
            metric = t.taskname
            value = taskY[metric]
            yield {'label':metric, 'y':value, 'x':datetime.datetime.fromtimestamp(float(t.start_time))}
            yield {'label':metric, 'y':value, 'x':datetime.datetime.fromtimestamp(float(t.finish_time))}
            yield {'label':metric, 'y':'',    'x':datetime.datetime.fromtimestamp(float(t.finish_time))}

