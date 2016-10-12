import pymongo
import time
from lib.common import *

def argparser(parser):
    parser = parser.add_parser('daemon')
    parser.set_defaults(func=daemon)

def daemon(db, fs, args):
    __globals = globals().copy()
    while True:
        cursor = db.run.find({'status' : 'created'}).sort([('runId',pymongo.ASCENDING)]).limit(1)
        try:
            run = next(cursor)
            runId = run['runId']
            config = matches_only_one_config(db, run['configId'])
            source = matches_only_one_source(fs, config['sourceId'])
            source = source.read()[:-1]
            print('Running %s' % run['runId'])
            _globals = __globals.copy()
            _globals['config'] = config
            _globals['run'] = run
            _globals['db'] = db
            _locals = _globals
            exec(source,_globals,_locals)
            db.run.update_one({'_id':run['_id']}, {"$set": {'status':'done'}})
        except StopIteration:
            print('Waiting for a new run')
            time.sleep(1)
