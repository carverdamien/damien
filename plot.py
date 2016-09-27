import pymongo, itertools, datetime

import plotly.offline # import download_plotlyjs, init_notebook_mode, iplot, plot
import plotly.graph_objs # import Scatter, Layout, Figure

curves = [{
    'label' : 'tunesysbench/23e73b86bc2a/mem/cache',
    'dbname' : 'tunesysbench',
    'collection' : 'dockerstats',
    'match' : {'Id' : {'$regex':'^23e73b86bc2a'}},
    'project' : {'x' : '$read', 'y': "$memory_stats.stats.cache"},
    'convert' : {'x' : lambda x : datetime.datetime.strptime(x[:-4], "%Y-%m-%dT%H:%M:%S.%f"), 'y' : lambda y : y}
}]

def XY(collection, dbname, match, project, convert, **kwargs):
    X = []
    Y = []
    db = pymongo.MongoClient()[dbname]
    for e in db[collection].aggregate([{"$match" : match}, {"$project": project}]):
        X.append(convert['x'](e['x']))
        Y.append(convert['y'](e['y']))
    return X, Y

def Scatter(label, **kwargs):
    X, Y = XY(**kwargs)
    return plotly.graph_objs.Scatter(x=X, y=Y, name=label, visible="legendonly")

data = [Scatter(**curve) for curve in curves]
layout = plotly.graph_objs.Layout(showlegend=True)
figure = plotly.graph_objs.Figure(data=data, layout=layout)
plotly.offline.plot(figure, filename='plotly.html', auto_open=False)
