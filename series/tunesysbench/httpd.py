@bottle.route('/tunesysbench/global/view.csv')
def httpd_tunesysbench():
    # x = dbsize
    # y = metric (perf, ressource)
    # label = [readonly, memlimit, aggregator, metric]
    alldbsize = sorted([e['_id']['dbsize']
                 for e in db.config.aggregate([{
                         '$group': {
                             '_id': {
                                 'dbsize':'$dbsize'
                             }
                         }
                 }])])
    allmem_limit = sorted([e['_id']['mem_limit']
                 for e in db.config.aggregate([{
                         '$group': {
                             '_id': {
                                 'mem_limit':'$mem_limit'
                             }
                         }
                 }])])
    def gen_perf_func(key):
        def func(run):
            T = []
            Y = []
            for e in db.sysbench.find({'Id':run['container']['Id']}):
                T.append(float(e['timestamp']))
                Y.append(float(e[key]))
            return T, Y
        func.func_name = key
        return func
    def memusage(run):
        T = []
        Y = []
        for e in db.dockerstats.find({'Id':run['container']['Id']}):
            T.append(e['read']) #datetime
            Y.append(e['memory_stats']['usage'])
        return T, Y
    def diskio(run):
        T = []
        Y = []
        for e in db.dockerstats.find({'Id':run['container']['Id']}):
            t = e['read']
            t = datetime.datetime.strptime(t[:-4], "%Y-%m-%dT%H:%M:%S.%f")
            T.append(t)
            Y.append(sum([data['value'] for data in e['blkio_stats']['io_service_bytes_recursive'] if data['op'] == 'Total']))
        dt = np.gradient([time.mktime(t.timetuple()) for t in T])
        Y = np.gradient(Y, dt)
        return T, Y
    allmetric = [gen_perf_func('rtps'), gen_perf_func('trps'), memusage, diskio]
    def max(T,M):
        return np.amax(M)
    def mean(T,M):
        return np.mean(M)
    allaggregator = [mean]
    directory = os.path.join(cache_dir, 'tunesysbench/global')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, 'view.csv')
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['x','y','label'])
            for dbsize in alldbsize:
                x = dbsize
                for mem_limit in allmem_limit:
                    for readonly, match_config in [('r',{'oltp_read_only':{'$exists':True}, 'mem_limit' : mem_limit}), ('rw',{'oltp_read_only':{'$exists':False}, 'mem_limit':mem_limit})]:
                        match_config['dbsize'] = dbsize
                        for config in db.config.find(match_config):
                            configId = config['configId']
                            for run in db.run.find({'configId':configId}):
                                for metric in allmetric:
                                    T,M = metric(run)
                                    for aggregate in allaggregator:
                                        y = aggregate(T,M)
                                        label = '.'.join([readonly,
                                                          str(mem_limit/(2**20))+'MB',
                                                          ''.join([aggregate.func_name,
                                                                   '(',
                                                                   metric.func_name,
                                                                   ')']),])
                                        csvwriter.writerow([x,y,label])
    with open(filename) as f:
        return f.read()
    return "oops"
@bottle.route('/sysbench')
def httpd_sysbench_listId():
    table = []
    for entry in db.sysbench.aggregate([{'$group': {'_id': {'Id':'$Id'}}}]):
        Id = entry['_id']['Id']
        run = next(db.run.find({'container.Id':Id}))
        config = next(db.config.find({'configId':run['configId']}))
        del config['sourceId']
        del config['configId']
        del config['_id']
        row = [str(config)]
        row += [Id[:4], HTML.link('inspect', '/dockercontainers/%s' % Id)]
        row += [HTML.link("%s.html" % stat,
                '/plotly/Scatter/dockerstats/%s/%s.html' % (Id, stat))
                for stat in ['cpu','memory','blkio', 'netio']]
        row += [HTML.link('perf.html', 
                '/'.join(['/plotly/Scatter/sysbench', Id, 'perf.html']))]
        table.append(row)
    return HTML.table(table)
@bottle.route('/sysbench/<Id>/perf.csv')
def httpd_sysbench_perf(Id):
    directory = os.path.join(cache_dir, 'sysbench', Id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, 'perf.csv')
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['x','y','label'])
            for entry in db.sysbench.find({'Id':Id}):
                del entry['Id']
                del entry['_id']
                x = datetime.datetime.utcfromtimestamp(float(entry['timestamp']))
                for key in entry:
                    if key == 'timestamp':
                        continue
                    y = entry[key]
                    label = '.'.join([Id[:4],key])
                    csvwriter.writerow([x,y,label])
    with open(filename) as f:
        return f.read()
