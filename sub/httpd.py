import pymongo
import bottle
import lib.HTML as HTML
import csv
import StringIO
import itertools
import datetime
import shutil
import os
import time

def argparser(parser):
    parser = parser.add_parser('httpd')
    parser.add_argument('--cache_dir', type=str, nargs='?', default='./httpd')
    parser.add_argument('--plugins', type=str, nargs='*', default=[])
    parser.set_defaults(func=httpd)

# @bottle.route('/clearCache')
# def clearCache():
#     shutil.rmtree(cache_dir)
#     os.makedirs(cache_dir)
#     return cache_index()

@bottle.route('/')
def httpd_cache_index():
    clear = HTML.link('clearCache', 'clearCache')
    table = [['cache', clear]]
    for dirName, subdirList, fileList in os.walk(cache_dir):
        for fname in fileList:
            link = os.path.join(os.path.join(*dirName.split('/')[2:]), fname)
            link = HTML.link(link, link)
            table += [[link]]
    return HTML.table(table)
@bottle.route('/run')

def httpd_run_list():
    table = [['runId', 'configId', 'config']]
    for run in db.run.find({'status':'done'}).sort([('_id',pymongo.DESCENDING)]):
        runId = run['runId']
        configId = run['configId']
        link_runId = HTML.link(runId[-4:],'/run/%s' % runId)
        link_configId = HTML.link(configId[:4],'/config/%s' % configId)
        config = next(db.config.find({'configId':configId},{'_id':0, 'sourceId':0, 'configId':0}))
        table.append([link_runId, link_configId, HTML.json(config)])
    return HTML.table(table)

PLOTABLES = {
    'dockerstats' : [
        {'plottype':'Scatter', 'name':'cpu'},
        {'plottype':'Scatter', 'name':'memory'},
        {'plottype':'Scatter', 'name':'blkio'},
        {'plottype':'Scatter', 'name':'netio'}
    ]
}

@bottle.route('/run/<runId>')
def httpd_run_show(runId):
    split = runId.split(',')
    if len(split) > 1:
        return "".join([httpd_run_show(runId) for runId in split])
    res = ""
    run = next(db.run.find({'runId':runId}))
    res += '<h1>Config</h1>'
    config = next(db.config.find({'configId':run['configId']}, {'_id':0, 'sourceId':0, 'configId':0}))
    res += HTML.json(config)
    containers = []
    if 'container' in run:
        containers = [run['container']]
    elif 'containers' in run:
        containers = run['containers']
    res += '<h1>Quick links</h1>'
    table = []
    for container in containers:
        row = [HTML.link(container['Id'][:4], '/dockercontainers/%s' % container['Id'])]
        for d in db.dockerstats.find({'Id':container['Id']}).limit(1):
            for collection in sorted(PLOTABLES.keys()):
                for plotable in PLOTABLES[collection]:
                    plottype = plotable['plottype']
                    name = plotable['name']
                    row.append(HTML.link("%s/%s.html" % (collection, name), '/plotly/%s/%s/%s/%s.html' % (plottype, collection, container['Id'], name)))
                    row.append(HTML.link("%s/%s.csv" % (collection, name), '/%s/%s/%s/%s.csv' % (plottype, collection, container['Id'], name)))
        table.append(row)
    res += HTML.table(table)
    res += '<h1>All plots</h1>'
    table = []
    for container in containers:
        row = []
        for d in db.dockerstats.find({'Id':container['Id']}).limit(1):
            for collection in sorted(PLOTABLES.keys()):
                for plotable in PLOTABLES[collection]:
                    plottype = plotable['plottype']
                    name = plotable['name']
                    row.append('<iframe src="%s" width=1200 height=600></iframe>' % '/plotly/%s/%s/%s/%s.html' % (plottype, collection, container['Id'], name))
                    #row.append(httpd_plot_any(plottype, collection, container['Id'], name))
        table.append(row)
    res += HTML.table(table)
    return res

@bottle.route('/dockercontainers/<Id>')
def httpd_dockercontainers(Id):
    for container in db.dockercontainers.find({'Id':Id}).limit(1):
        return str(container)
    return "Not Found"

@bottle.route('/dockerstats/<listId>/<stat>.csv')
def httpd_dockerstats_csv(listId,stat):
    if stat not in ['memory', 'blkio']:
        return "x,y,label\n0,0,Oops:%s not implemented" % stat
    directory = os.path.join(cache_dir,'dockerstats',listId)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, stat + '.csv')
    # cache miss
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow(['x','y','label'])
            for Id in listId.split(','):
                label = [Id[:4]]
                if stat == 'memory':
                    X = []
                    YPGPGIN = []
                    YPGPGOUT = []
                    for entry in db.dockerstats.find({'Id':Id},{'memory_stats':1,'read':1}):
                        x = entry['read']
                        x = datetime.datetime.strptime(x[:-4], "%Y-%m-%dT%H:%M:%S.%f")
                        X.append(x)
                        y = entry['memory_stats']
                        def flat(key, y):
                            if type(y) == dict:
                                for k, v in y.iteritems():
                                    flat(key+[k], v)
                            elif type(y) == list:
                                print(y)
                            else:
                                if key[-1] == 'pgpgin':
                                    YPGPGIN.append(y)
                                elif key[-1] == 'pgpgout':
                                    YPGPGOUT.append(y)
                                csvwriter.writerow([x,y,".".join(key)])
                        flat(label,y)
                    dt = np.gradient([time.mktime(x.timetuple()) for x in X])
                    dindt = np.gradient(YPGPGIN, dt)
                    for x,y in itertools.izip(X,dindt):
                        csvwriter.writerow([x,y,".".join(label + ['dpgpgin/dt'])])
                    doutdt = np.gradient(YPGPGOUT, dt)
                    for x,y in itertools.izip(X,doutdt):
                        csvwriter.writerow([x,y,".".join(label + ['dpgpgout/dt'])])
                    din = np.gradient(YPGPGIN)
                    doutdin = np.gradient(YPGPGOUT,din)
                    for x,y in itertools.izip(X,doutdin):
                        csvwriter.writerow([x,y,".".join(label + ['dpgpgout/dpgpgin'])])
                    dout = np.gradient(YPGPGOUT)
                    dindout = np.gradient(YPGPGIN,dout)
                    for x,y in itertools.izip(X,dindout):
                        csvwriter.writerow([x,y,".".join(label + ['dpgpgin/dpgpgout'])])
                elif stat == 'blkio':
                    X = []
                    YREAD = []
                    YWRITE = []
                    for entry in db.dockerstats.find({'Id':Id},{'blkio_stats':1,'read':1}):
                        x = entry['read']
                        x = datetime.datetime.strptime(x[:-4], "%Y-%m-%dT%H:%M:%S.%f")
                        yr = 0
                        yw = 0
                        for data in entry['blkio_stats']['io_service_bytes_recursive']:
                            if data['op'] == 'Write':
                                yw += data['value']
                            elif data['op'] == 'Read':
                                yr += data['value']
                        X.append(x)
                        YWRITE.append(yw)
                        YREAD.append(yr)
                    dx = np.gradient([time.mktime(x.timetuple()) for x in X])
                    Y = np.gradient(np.array(YREAD)+np.array(YWRITE),dx)
                    YWRITE = np.gradient(YWRITE, dx)
                    YREAD = np.gradient(YREAD, dx)
                    for x,y in itertools.izip(X,YWRITE):
                        csvwriter.writerow([x,y,".".join(label+['w'])])
                    for x,y in itertools.izip(X,YREAD):
                        csvwriter.writerow([x,y,".".join(label+['r'])])
                    for x,y in itertools.izip(X,Y):
                        csvwriter.writerow([x,y,".".join(label+['total'])])
    with open(filename) as f:
        return f.read()
    return "x,y,label\n0,0,oops\n1,1,oops\n"

@bottle.route('/plotly/<plottype>/<collection>/<selector>/<filename>.html')
def httpd_plot_any(plottype, collection, selector, filename):
    directory_csv = os.path.join(cache_dir, collection, selector)
    filename_csv = os.path.join(directory_csv, filename + '.csv')
    directory_html = os.path.join(cache_dir, 'plotly', plottype, collection, selector)
    filename_html = os.path.join(directory_html, filename + '.html')
    if os.path.exists(filename_html) and collection not in ['analytics']:
        with open(filename_html) as f:
            return f.read()
    elif not os.path.exists(directory_html):
        os.makedirs(directory_html)
    if not os.path.exists(filename_csv):
        environ = {'REQUEST_METHOD' : 'GET', 'PATH_INFO' : '/%s/%s/%s.csv' % (collection, selector, filename)}
        target, args = bottle.default_app().router.match(environ)
        csv = target.call(**args)
        df = pd.read_csv(StringIO.StringIO(csv))
    else:
        df = pd.read_csv(filename_csv)
    def label_sel_generator(df):
        for label in np.unique(df['label']):
            sel = df['label'] == label
            yield label, sel
    def X_Y_label_generator(df):
        for label, sel in label_sel_generator(df):
            X = df['x'][sel]
            Y = df['y'][sel]
            text = None
            if 'text' in df:
                text = df['text'][sel]
            yield X, Y, text, label
    data = [plotly.graph_objs.Scatter(x=X, y=Y, text=text, name=label, visible="legendonly") for (X,Y,text,label) in X_Y_label_generator(df)]
    annotations = []
    if 'annotation' in df:
        annotations = [ {'x':x,
                         'y': y,
                         'xref':'x',
                         'yref':'y',
                         'text':annotation,
                         'showarrow':False,
                         'arrowhead':0
                     } for x, y, annotation in itertools.izip(df['x'], df['y'], df['annotation'])]
    layout = plotly.graph_objs.Layout(annotations=annotations, showlegend=True, yaxis={'rangemode':'tozero'})
    figure = plotly.graph_objs.Figure(data=data, layout=layout)
    plotly.offline.plot(figure, filename=filename_html, auto_open=False)
    with open(filename_html) as f:
        return f.read()
    return "Oops"

@bottle.route('/config')
def httpd_config_list():
    table = [['configId', 'sourceId', 'values']]
    for config in db.config.find({},{'_id':0}):
        configId = config['configId']
        del config['configId']
        sourceId = config['sourceId']
        del config['sourceId']
        values = str(config)
        link_configId = HTML.link(configId[:4], '/config/%s' % configId)
        link_sourceId = HTML.link(sourceId[:4], '/source/%s' % sourceId)
        table.append([link_configId, link_sourceId, str(config)])
    return HTML.table(table)

@bottle.route('/config/<configId>')
def httpd_config_show(configId):
    table = [['runId', 'status', 'extra']]
    for run in db.run.find({'configId':configId}, {'_id':0, 'configId':0}):
        runId = run['runId']
        del run['runId']
        status = run['status']
        del run['status']
        extra = str(run)
        link_runId = HTML.link(runId[-4:], '/run/%s' % runId)
        table.append([link_runId, status, extra])
    return HTML.table(table)

@bottle.route('/source/<sourceId>')
def httpd_source_show(sourceId):
    source = matches_only_one_source(fs, sourceId)
    return source.read()[:-1]

@bottle.route('/analytics/<name>/<view>.csv')
def httpd_analytics(name, view):
    directory_csv = os.path.join(cache_dir, 'analytics', name)
    if not os.path.exists(directory_csv):
        os.makedirs(directory_csv)
    filename_csv = os.path.join(directory_csv, view + '.csv.tmp') # TODO: cachable?
    analytics = next(db.analytics.find({'name':name}))
    dataref = analytics['dataref']
    view = analytics['view'][view]
    _globals = globals().copy()
    exec(view, _globals, _globals)
    view = _globals['view']
    with open(filename_csv, 'w') as f:
        csvwriter = csv.writer(f)
        header = None
        for data in dataref:
            res = view(data)
            if header == None:
                header = res.keys()
                csvwriter.writerow(header)
            csvwriter.writerow([res[h] for h in header])
    with open(filename_csv) as f:
        return f.read()
    return "x,y,label\n0,0,oops\n"

def httpd(_db, fs, args):
    import pandas
    global pd
    pd = pandas
    import numpy
    global np
    np = numpy
    import plotly as _plotly
    global plotly
    plotly = _plotly
    for plugin in args.plugins:
        for dirName, subdirList, fileList in os.walk(plugin):
            for fname in fileList:
                if fname == 'httpd.py':
                    with open(os.path.join(dirName, fname)) as f:
                        exec(f.read())
    global cache_dir
    global db
    db = _db
    cache_dir = args.cache_dir
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    bottle.run(host='0.0.0.0', port=8080, debug=True)
