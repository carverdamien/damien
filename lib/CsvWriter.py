import threading, Queue, csv

class CsvWriter(threading.Thread):
    def __init__(self, filename):
        super(CsvWriter, self).__init__()
        self.daemon = True
        self.filename = filename
        self.f = open(filename, 'w')
        self.writer = csv.writer(self.f)
        self.queue = Queue.Queue(maxsize=0)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()

    def join(self):
        self.queue.join()
        self.f.close()

    def run(self):
        writer = self.writer
        dic = self.queue.get()
        header = sorted(dic.keys())
        writer.writerow(header)
        writer.writerow([dic[h] for h in header])
        self.queue.task_done()
        while True:
            dic = self.queue.get()
            try:
                writer.writerow([dic[h] for h in header])
            except Exception as e: print(e)
            self.queue.task_done()
    
    def write(self, **kwargs):
        self.queue.put_nowait(kwargs)
