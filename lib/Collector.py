import threading, time, datetime

class Collector(threading.Thread):
    def __init__(self, data_writer, sleep_delay=1):
        super(Collector, self).__init__()
        self.data_writer = data_writer
        self.sleep_delay = sleep_delay
        self.exitEvent = threading.Event()
        
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exitEvent.set()
        self.join()

    def collect_function(self):
        return [{'timestamp':time.time(), 'foo' : random.random() }]

    def run(self):
        while not self.exitEvent.is_set():
            time.sleep(self.sleep_delay)
            for values in self.collect_function():
                timestamp = datetime.datetime.fromtimestamp(float(values['timestamp']))
                for metric in values:
                    if metric == 'timestamp':
                        continue
                    value = values[metric]
                    self.data_writer.write(label=metric, y=value, x=timestamp)

    def exit(self):
        self.exitEvent.set()
