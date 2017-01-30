def view(dataref):
    def one(runId):
        run = next(db.run.find({'runId':runId}))
        config = next(db.config.find({'configId':run['configId']}))
        x = int(config['containers'][1]['host_config']['mem_limit'])
        key = 'ops_s'
        data = np.array([float(entry[key]) for container in run['containers'] for entry in db.memtier.find({'Id':container['Id']})])
        y = np.mean(data)
        annotation = '<a href="http://indium.rsr.lip6.fr/run/%s">X</a>' %  (runId)
        return {'x':x, 'y':y, 'label':'.'.join(['mean(%s)' % key]), 'annotation':annotation}
    ret = []
    for data in dataref:
        try:
            ret.append(one(data))
        except Exception as e:
            pass
    return sorted(ret, key=lambda e: e['x'])
