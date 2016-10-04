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
