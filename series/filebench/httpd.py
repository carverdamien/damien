@bottle.route('/filebench')
def httpd_filebench_listId():
    table = []
    def append(table, run):
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
                '/'.join(['/plotly/Scatter/filebench', Id, 'perf.html']))]
        table.append(row)
    for entry in db.filebench.aggregate([{'$group': {'_id': {'Id':'$Id'}}}]):
        print(entry)
        Id = entry['_id']['Id']
        for run in db.run.find({'containers':{'$exists':True}}):
            for container in run['containers']:
                if Id == container['Id']:
                    append(table, run)
    return HTML.table(table)

@bottle.route('/filebench/<Id>/perf.csv')
def httpd_filebench_perf(Id):
    directory = os.path.join(cache_dir, 'filebench', Id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, 'perf.csv')
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['x','y','label'])
            for flowop in [f['_id']['flowop'] for f in db.filebench.aggregate([{'$match':{'Id':Id}}, {'$group': {'_id': {'flowop':'$flowop'}}}])]:
                for entry in db.filebench.find({'Id':Id, 'flowop':flowop}):
                    del entry['Id']
                    del entry['_id']
                    del entry['flowop']
                    profile = entry['profile']
                    del entry['profile']
                    x = datetime.datetime.utcfromtimestamp(float(entry['timestamp']))
                    for key in entry:
                        if key == 'timestamp':
                            continue
                        y = entry[key]
                        if y != '':
                            label = '.'.join([Id[:4],profile,flowop,key])
                            csvwriter.writerow([x,y,label])
    with open(filename) as f:
        return f.read()
