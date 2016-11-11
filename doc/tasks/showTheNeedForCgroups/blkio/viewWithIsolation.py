def view(runId):
    flowop = 'IO Summary'
    key = 'mb/s'
    profiles = ['procA', 'procB']
    def perf(profile, runId, flowop, key):
        run = next(db.run.find({'runId':runId}))        
        data = np.array([float(entry[key]) for container in run['containers'] for entry in db.filebench.find({'Id':container['Id'], 'flowop':flowop, 'profile':profile})])
        return np.mean(data)
    def rate(profile, runId, flowop, key):
        run = next(db.run.find({'runId':runId}))        
        for container in run['containers']:
            for entry in db.filebench.find({'Id':container['Id'], 'flowop':flowop, 'profile':profile}):
                Id = entry['Id']
                for entry in db.dockercontainers.find({'Id':Id}):
                    rate = entry['HostConfig']['BlkioDeviceReadBps'][0]['Rate']
                    return rate
    perfA = perf(profiles[0], runId, flowop, key)
    perfB = perf(profiles[1], runId, flowop, key)
    rateA = rate(profiles[0], runId, flowop, key)
    rateB = rate(profiles[1], runId, flowop, key)
    annotation = '<a href="http://indium.rsr.lip6.fr/run/%s">X</a>' %  (runId)
    yield {'x':rateA+rateB, 'y':perfA, 'label':'.'.join(['procA.mean(%s in %s)' % (flowop,key)]), 'annotation':annotation}
    yield {'x':rateA+rateB, 'y':perfB, 'label':'.'.join(['procB.mean(%s in %s)' % (flowop,key)]), 'annotation':annotation}
