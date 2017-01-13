PLOTABLES['memtier'] = [{'plottype':'Scatter', 'name':'perf'}]

@bottle.route('/memtier/<Id>/perf.csv')
def httpd_sysbench_perf(Id):
    directory = os.path.join(cache_dir, 'memtier', Id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, 'perf.csv')
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['x','y','label'])
            haveData = False
            for entry in db.memtier.find({'Id':Id}):
                del entry['Id']
                del entry['_id']
                x = datetime.datetime.utcfromtimestamp(float(entry['timestamp']))
                for key in entry:
                    if key == 'timestamp':
                        continue
                    y = entry[key]
                    label = '.'.join([Id[:4],key])
                    csvwriter.writerow([x,y,label])
                    haveData = True
            if not haveData:
                csvwriter.writerow([0,0,'No Data'])
    with open(filename) as f:
        return f.read()
