def view(dataref):
    runIdIsolated, runIdGrouped = dataref.split(',')
    flowop = 'IO Summary'
    key = 'mb/s'
    profiles = ['inmemory', 'outofmemory']
    def perf(profile, runId, flowop, key):
        run = next(db.run.find({'runId':runId}))        
        data = np.array([float(entry[key]) for container in run['containers'] for entry in db.filebench.find({'Id':container['Id'], 'flowop':flowop, 'profile':profile})])
        return np.mean(data)
    deltaA = perf(profiles[0], runIdIsolated, flowop, key) - perf(profiles[0], runIdGrouped, flowop, key)
    deltaB = perf(profiles[1], runIdIsolated, flowop, key) - perf(profiles[1], runIdGrouped, flowop, key)
    annotation = '<a href="http://indium.rsr.lip6.fr/run/%s,%s">X</a>' %  (runIdIsolated, runIdGrouped)
    return {'x':deltaA, 'y':deltaB, 'label':'.'.join(['delta',flowop,key]), 'annotation':annotation}
