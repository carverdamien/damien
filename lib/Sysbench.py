import Task
import os, subprocess, time, pwd, parse, threading, tempfile

expected_v04_output = \
"""OLTP test statistics:
{:s}queries performed:
{:s}read:{:s}{read_queries}
{:s}write:{:s}{write_queries}
{:s}other:{:s}{other_queries}
{:s}total:{:s}{total_queries}
{:s}transactions:{:s}{transactions}{:s}({transactions_per_sec} per sec.)
{:s}deadlocks:{:s}{deadlocks}{:s}({deadlocks_per_sec} per sec.)
{:s}read/write requests:{:s}{rw_requests}{:s}({rw_requests_per_sec} per sec.)
{:s}other operations:{:s}{other_operations}{:s}({other_operations_per_sec} per sec.)

Test execution summary:
{:s}total time:{:s}{total_time_in_sec}s
{:s}total number of events:{:s}{total_number_of_events}
{:s}total time taken by event execution:{:s}{total_time_taken_by_event_execution}
{:s}per-request statistics:
{:s}min:{:s}{min_response_time_in_ms}ms
{:s}avg:{:s}{avg_response_time_in_ms}ms
{:s}max:{:s}{max_response_time_in_ms}ms
{:s}approx.{:s}{percentile} percentile:{:s}{percentile_response_time_in_ms}ms

Threads fairness:
{:s}events (avg/stddev):{:s}{avg_event_fairness}/{stddev_event_fairness}
{:s}execution time (avg/stddev):{:s}{avg_execution_time_fairness}/{stddev_execution_time_fairness}

"""

expected_v05_final_output = \
"""
OLTP test statistics:
{:s}queries{:s}performed:
{:s}read:{:s}{read_queries}
{:s}write:{:s}{write_queries}
{:s}other:{:s}{other_queries}
{:s}total:{:s}{total_queries}
{:s}transactions:{:s}{transactions}{:s}({transactions_per_sec} per sec.)
{:s}read/write{:s}requests:{:s}{rw_requests}{:s}({rw_requests_per_sec} per sec.)
{:s}other{:s}operations:{:s}{other_operations}{:s}({other_operations_per_sec}{:s}per{:s}sec.)
{:s}ignored{:s}errors:{:s}{ignored_errors}{:s}({ignored_errors_per_sec} per sec.)
{:s}reconnects:{:s}{reconnects}{:s}({reconnects_per_sec} per sec.)

General{:s}statistics:
{:s}total{:s}time:{:s}{total_time_in_sec}s
{:s}total{:s}number{:s}of{:s}events:{:s}{total_number_of_events}
{:s}total{:s}time{:s}taken{:s}by{:s}event{:s}execution:{:s}{total_time_taken_by_event_execution}s
{:s}response{:s}time:
{:s}min:{:s}{min_response_time_in_ms}ms
{:s}avg:{:s}{avg_response_time_in_ms}ms
{:s}max:{:s}{max_response_time_in_ms}ms
{:s}approx.{:s}{percentile} percentile:{:s}{percentile_response_time_in_ms}ms

Threads{:s}fairness:
{:s}events (avg/stddev):{:s}{avg_event_fairness}/{stddev_event_fairness}
{:s}execution time (avg/stddev):{:s}{avg_execution_time_fairness}/{stddev_execution_time_fairness}

"""

expected_v05_intermediate_output = \
"""
[{}] timestamp: {timestamp}, threads: {threads}, tps: {trps}, reads: {rdps}, writes: {wrps}, response time: {rtps}ms ({}%), errors: {errps}, reconnects:  {recops}
"""

global ___next_port
___next_port = 22345
def get_next_port():
    global ___next_port
    ___next_port += 1
    return ___next_port

class Sysbench(Task.Task):
    def __init__(self, name, cgroup, working_directory, **args):
        self.oltp_read_only = "on"
        super(Sysbench, self).__init__(name, cgroup, working_directory, **args)
        self.port = str(get_next_port())
        self.dbsize = int(self.dbsize) # Not optional
        self.num_threads = int(self.num_threads) # Not optional
        self.binpath = './submodules/sysbench/sysbench/sysbench'
        self.luapath = './submodules/sysbench/sysbench/tests/db/oltp.lua'
        self.dbname = "db%s" % self.port
        self.datadir = os.path.join(self.working_directory, '%s.data' % self.port )
        self.socket = '%s.sock' % self.port
        self.pid_file = '%s.pid' % self.port
        self.log_error = '%s.log' % self.port
        self.call_init_datadir = ['sudo', 'mysqld', '--initialize-insecure', '--datadir=%s' % self.datadir]
        self.call_install_db = ['sudo', 'mysql_install_db', '--datadir=%s' % self.datadir]
        self.call_start_server = ['sudo', 'mysqld_safe', '--no-defaults', '--skip-syslog', '--pid-file=%s' % self.pid_file, '--log-error=%s' % self.log_error,  '--socket=%s' % self.socket, '--port=%s' % self.port, '--datadir=%s' % self.datadir]
        self.call_check_server_status = ['sudo', 'mysql', '--socket=%s' % os.path.join(self.datadir, self.socket)]
        self.call_stop_server = ['sudo', 'mysqladmin','shutdown', '--socket=%s' % os.path.join(self.datadir, self.socket), '--port=%s' % self.port]
        self.call_create_db = ['sudo', 'mysql', '--socket=%s' % os.path.join(self.datadir, self.socket), '-e', 'CREATE DATABASE %s' % self.dbname]
        self.call_fill_db = ['sudo', self.binpath, '--test=%s' % self.luapath, '--oltp-table-size=%d' % self.dbsize, '--mysql-db=%s' % self.dbname, '--mysql-socket=%s' % os.path.join(self.datadir, self.socket), '--mysql-user=root', '--mysql-password=', 'prepare']
        self.proc_server = None
        self.final_output_parser = parse.compile(expected_v05_final_output)
        self.intermediate_output_parser = parse.compile(expected_v05_intermediate_output)
        self.post_process = []
    
    def wait_for_server_to_start(self):
        while True:
            p = subprocess.Popen(self.call_check_server_status, stdin=open('/dev/null'))
            p.wait()
            if p.returncode == 0:
                print('mysqld started!')
                break
            else:
                print('Waiting for mysqld to start')
                time.sleep(1)

    def open_working_directory(self):
        super(Sysbench, self).open_working_directory()
        os.makedirs(self.datadir)
        os.chown(self.datadir, pwd.getpwnam('mysql').pw_uid, pwd.getpwnam('mysql').pw_gid)
        self.cgroup.Popen(self.call_init_datadir).wait()
        self.cgroup.check_call(self.call_install_db)
        self.proc_server = self.cgroup.Popen(self.call_start_server)
        self.wait_for_server_to_start()
        self.cgroup.check_call(self.call_create_db)
        self.cgroup.check_call(self.call_fill_db)
        self.cgroup.check_call(self.call_stop_server)
        self.proc_server.wait()
        self.proc_server = None

    def open_workers(self):
        super(Sysbench, self).open_workers()
        self.proc_server = self.cgroup.Popen(self.call_start_server)
        self.wait_for_server_to_start()

    def close_workers(self):
        self.cgroup.check_call(self.call_stop_server)
        self.proc_server.wait()
        self.proc_server = None
        super(Sysbench, self).close_workers()

    def close_working_directory(self):
        for func, args, kwargs in self.post_process:
            func(*args, **kwargs)
        super(Sysbench, self).close_working_directory()

    def parse_and_report(self, toparse, start, finish):
        d = self.final_output_parser.search(toparse).named
        for name in d:
            value = d[name]
            self.report(name, value, start, finish)
        for d in self.intermediate_output_parser.findall(toparse):
            d = d.named
            start = float(d['timestamp'])
            finish = start
            del d['timestamp']
            for name in d:
                value = d[name]
                self.report(name, value, start, finish)
        self.reportEOW(finish)

    def wustop(self):
        call = ['sudo', self.binpath, '--test=%s' % self.luapath, '--report-interval=1', '--oltp-table-size=%d' % self.dbsize, '--mysql-db=%s' % self.dbname, '--mysql-socket=%s' % os.path.join(self.datadir, self.socket), '--mysql-user=root', '--mysql-password=', '--max-time=0', '--oltp-read-only=%s' % self.oltp_read_only, '--max-requests=0', '--num-threads=%d' % self.num_threads, 'run']
        assert(not self.wrkEvent.is_set())
        self.wrkEvent.set()
        start = time.time()
        stdout = tempfile.TemporaryFile()
        p = subprocess.Popen(call, stdin=subprocess.PIPE, stdout=stdout)
        self.stopEvent.wait()
        p.stdin.write('q\n')
        p.stdin.flush()
        self.stopEvent.clear()
        p.wait()
        finish = time.time()
        def todo():
            stdout.seek(0)
            toparse = stdout.read()
            stdout.close()
            self.parse_and_report(toparse, start, finish)
        self.post_process.append((todo,[],{}))

    def wuoot(self, duration):
        call = ['sudo', self.binpath, '--test=%s' % self.luapath, '--report-interval=1', '--oltp-table-size=%d' % self.dbsize, '--mysql-db=%s' % self.dbname, '--mysql-socket=%s' % os.path.join(self.datadir, self.socket), '--mysql-user=root', '--mysql-password=', '--max-time=%d' % duration, '--oltp-read-only=%s' % self.oltp_read_only, '--max-requests=0', '--num-threads=%d' % self.num_threads, 'run']
        start = time.time()
        stdout = tempfile.TemporaryFile()
        p = subprocess.Popen(call, stdout=stdout)
        p.wait()
        finish = time.time()
        def todo():
            stdout.seek(0)
            toparse = stdout.read()
            stdout.close()
            self.parse_and_report(toparse, start, finish)
        self.post_process.append((todo,[],{}))

    def wuoow(self, ops):
        call = ['sudo', self.binpath, '--test=%s' % self.luapath, '--report-interval=1', '--oltp-table-size=%d' % self.dbsize, '--mysql-db=%s' % self.dbname, '--mysql-socket=%s' % os.path.join(self.datadir, self.socket), '--mysql-user=root', '--mysql-password=', '--max-time=0', '--oltp-read-only=%s' % self.oltp_read_only, '--max-requests=%d' % ops, '--num-threads=%d' % self.num_threads, 'run']
        start = time.time()
        stdout = tempfile.TemporaryFile()
        p = subprocess.Popen(call, stdout=stdout)
        p.wait()
        finish = time.time()
        def todo():
            stdout.seek(0)
            toparse = stdout.read()
            stdout.close()
            self.parse_and_report(toparse, start, finish)
        self.post_process.append((todo,[],{}))
