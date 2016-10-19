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
    for run in db.run.find({'status':'done'}):
        runId = run['runId']
        configId = run['configId']
        link_runId = HTML.link(runId[-4:],'/run/%s' % runId)
        link_configId = HTML.link(configId[:4],'/config/%s' % configId)
        config = next(db.config.find({'configId':configId},{'_id':0, 'sourceId':0, 'configId':0}))
        table.append([link_runId, link_configId, HTML.json(config)])
    return HTML.table(table)

@bottle.route('/run/<runId>')
def httpd_run_show(runId):
    table = []
    run = next(db.run.find({'runId':runId}))
    containers = []
    if 'container' in run:
        containers = [run['container']]
    elif 'containers' in run:
        containers = run['containers']
    for container in containers:
        row = ['container', HTML.link('inspect', '/dockercontainers/%s' % container['Id'])]
        for d in db.dockerstats.find({'Id':container['Id']}).limit(1):
            row += [HTML.link("%s.html" % stat,
                    '/plotly/Scatter/dockerstats/%s/%s.html' % (container['Id'], stat))
                    for stat in ['cpu','memory','blkio', 'netio']]
            row += [HTML.link("%s.csv" % stat,
                    '/dockerstats/%s/%s.csv' % (container['Id'], stat))
                    for stat in ['cpu','memory','blkio', 'netio']]
        table.append(row)
    return HTML.table(table)

@bottle.route('/dockercontainers/<Id>')
def httpd_dockercontainers(Id):
    for container in db.dockercontainers.find({'Id':Id}).limit(1):
        return str(container)
    return "Not Found"

@bottle.route('/dockerstats/<listId>/<stat>.csv')
def httpd_dockerstats_csv(listId,stat):
    if stat not in ['memory', 'blkio']:
        return "Oops"
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
    if os.path.exists(filename_html):
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
            yield X, Y, label
    data = [plotly.graph_objs.Scatter(x=X, y=Y, name=label, visible="legendonly") for (X,Y,label) in X_Y_label_generator(df)]
    layout = plotly.graph_objs.Layout(showlegend=True)
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
    for dirName, subdirList, fileList in os.walk('./series'):
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
