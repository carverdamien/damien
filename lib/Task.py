import os, shutil, time, threading, pydoc, csv, datetime

class Task(object):
    def __init__(self, name, cgroup, working_directory, datawriter=None, **args):
        """
        cgroup : main threads (like server) must run in this cgroup.
        master threads (like client) should not run in this cgroup.
        cgroup should be already created and initialized.

        working_directory : all data must reside in this directory. (this allows simple tmpfs/ssd/spindisk configurations)
        """
        self.datawriter = datawriter
        self.name = name
        self.metrics_reported = set()
        self.cgroup = cgroup
        self.working_directory = working_directory
        self.wrkEvent = threading.Event()
        self.wrkEvent.clear()
        self.stopEvent = threading.Event()
        self.stopEvent.clear()
        for k in args:
            setattr(self, k, args[k])
    
    def report(self, metric, value, start, finish):
        metric = "/".join([self.name, metric])
        self.metrics_reported.add(metric)
        self.datawriter.write(label=metric, y=value, x=datetime.datetime.fromtimestamp(float(start)))
        self.datawriter.write(label=metric, y=value, x=datetime.datetime.fromtimestamp(float(finish)))

    def reportEOW(self, finish):
        value = ''
        for metric in self.metrics_reported:
            self.datawriter.write(label=metric, y=value, x=datetime.datetime.fromtimestamp(float(finish)))

    def open_working_directory(self):
        """
        Initialize data in working_directory.
        """
        os.makedirs(self.working_directory)
        os.chmod(self.working_directory, 0o777)

    def close_working_directory(self):
        """
        Clean working_directory.
        """
        shutil.rmtree(self.working_directory)

    def open_workers(self):
        """
        Create working process/threads
        """
        pass

    def close_workers(self):
        """
        Destroy working process/threads
        """
        pass

    def stop(self):
        """
        Ask workers to stop.
        """
        self.wrkEvent.wait()
        self.wrkEvent.clear()
        assert(not self.stopEvent.is_set())
        self.stopEvent.set()
        pass

    def wustop(self, ops=1):
        """
        wustop : work_until_Stopped
        Ask workers to work until self.stop() is called.
        This function blocks until self.stop() is called from another thread.
        """
        assert(not self.wrkEvent.is_set())
        self.wrkEvent.set()
        start = time.time()
        name = 'work until stopped'
        value = 0
        while not self.stopEvent.is_set():
            time.sleep(ops) # working so hard
            value += ops
        finish = time.time()
        self.report(name, value, start, finish)
        self.stopEvent.clear()
        pass

    def wuoot(self, duration, ops=1):
        """
        wuoot : work_until_Out_Of_Time
        Ask workers to work for duration seconds and count the number of operations.
        This function blocks until duration seconds passes.
        """
        start = time.time()
        name = 'work until out of time'
        value = 0
        finish = start
        while (finish - start) < duration:
            time.sleep(ops) # working so hard
            value += ops
            finish = time.time()
        self.report(name, value, start, finish)
        pass

    def wuoow(self, ops):
        """
        wuoow : work_until_Out_Of_Work
        Ask workers to do ops amount of operations and record the completion time.
        This function blocks until ops amount of operation is done.
        """
        start = time.time()
        name = 'work until out of work'
        value = ops
        time.sleep(ops) # working so hard
        finish = time.time()
        self.report(name, value, start, finish)
        pass

def load(name, task):
    toload = task['module']+"."+task['class']
    loaded = pydoc.locate(toload)
    if loaded == None:
        raise Exception('Cannot find %s', toload)
    return loaded(name=name, cgroup=task['cgroup'], working_directory=task['working_directory'], **task['args'])
