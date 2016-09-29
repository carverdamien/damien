import pymongo, itertools, datetime, time
import numpy as np
import plotly.offline # import download_plotlyjs, init_notebook_mode, iplot, plot
import plotly.graph_objs # import Scatter, Layout, Figure

convert_read_to_datetime = lambda x : datetime.datetime.strptime(x[:-4], "%Y-%m-%dT%H:%M:%S.%f")
convert_datetime_to_timestamp = lambda x : time.mktime(x.timetuple())
convert_timestamp_to_datetime = lambda x : datetime.datetime.utcfromtimestamp(float(x))

containers = [{'$regex':'^8e700'}, {'$regex':'^ac133'}]
curves = [{
    'label' : '%s.trps' % Id['$regex'],
    'dbname' : 'tunesysbench',
    'collection' : 'sysbench',
    'match' : {'Id' : Id},
    'project' : {'x' : '$timestamp', 'y': "$trps"},
    'convert' : lambda x,y : (convert_timestamp_to_datetime(x), y)
} for Id in containers]
curves += [{
    'label' : '%s%s' % (Id['$regex'], metric),
    'dbname' : 'tunesysbench',
    'collection' : 'dockerstats',
    'match' : {'Id' : Id},
    'project' : {'x' : '$read', 'y': "$memory_stats%s" % metric},
    'convert' : lambda x,y : (convert_read_to_datetime(x), y)
} for Id in containers for metric in ['.usage','.limit', '.stats.cache', '.stats.active_file', '.stats.inactive_file']]

curves += [{
    'label' : '%s%s' % (Id['$regex'], metric),
    'dbname' : 'tunesysbench',
    'collection' : 'dockerstats',
    'match' : {'Id' : Id},
    'project' : {'x' : '$read', 'y': "$blkio_stats%s" % metric},
    'convert' : lambda x,y : (convert_read_to_datetime(x),y[4]['value']),
    'vector' : lambda X,Y : (X, np.gradient(Y, np.gradient([convert_datetime_to_timestamp(x) for x in X])))
} for Id in containers for metric in ['.io_service_bytes_recursive']]

def XY(collection, dbname, match, project, convert=lambda x,y : (x,y), **kwargs):
    X = []
    Y = []
    db = pymongo.MongoClient()[dbname]
    for e in db[collection].aggregate([{"$match" : match}, {"$project": project}]):
        x , y = convert(e['x'], e['y'])
        X.append(x)
        Y.append(y)
    return X, Y

def Scatter(label, vector=lambda X,Y : (X,Y), **kwargs):
    X, Y = vector(*XY(**kwargs))
    return plotly.graph_objs.Scatter(x=X, y=Y, name=label, visible="legendonly")

data = [Scatter(**curve) for curve in curves]
layout = plotly.graph_objs.Layout(showlegend=True)
figure = plotly.graph_objs.Figure(data=data, layout=layout)
plotly.offline.plot(figure, filename='plotly.html', auto_open=False)
