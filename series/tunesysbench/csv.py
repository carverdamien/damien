import pymongo
import numpy as np
#import plotly.offline # import download_plotlyjs, init_notebook_mode, iplot, plot
#import plotly.graph_objs # import Scatter, Layout, Figure

dbname = 'tunesysbench'
sourceId = '7e6576fbfb2d41b3c9be1470641e33cb5c9e54cad5aeb6392193ad8c'

def list_config(db):
    for config in db.config.find({'sourceId' : sourceId, 'threads':8}): yield config

def get_y(db, containerId):
    Y = []
    key = 'trps'
    for e in db.sysbench.find({'Id':containerId}, {'_id':0, key:1}):
        Y.append(float(e[key]))
    return np.mean(Y)

def list_run(db):
    print('x,y,label')
    for config in list_config(db):
        for run in db.run.find({'configId' : config['configId'], 'status' : 'done'}):
            dbsize = config['dbsize']
            mem_limit = config['mem_limit']
            containerId = run['container']['Id']
            y = get_y(db, containerId)
            print("%s,%s,%s" % (dbsize, y, mem_limit))

db = pymongo.MongoClient()[dbname]
list_run(db)
