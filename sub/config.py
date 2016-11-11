from lib.common import *
import json
import hashlib
import tabulate

def argparser(parser):
    parser = parser.add_parser('config')
    subparsers = parser.add_subparsers()
    #
    parser = subparsers.add_parser('add')
    parser.set_defaults(func=add)
    parser.add_argument('json_file', type=str)
    #
    parser = subparsers.add_parser('ls')
    parser.set_defaults(func=ls)
    #
    parser = subparsers.add_parser('show')
    parser.set_defaults(func=show)
    parser.add_argument('configId', type=str)
    #
    parser = subparsers.add_parser('rm')
    parser.set_defaults(func=rm)
    parser.add_argument('configId', type=str)

def add(db, fs, args):
    with open(args.json_file) as json_file:
        config = json.load(json_file)
        if 'configId' in config:
            del config['configId']
        configId = hashlib.sha224(json.dumps(config,sort_keys=True)).hexdigest()
        config['configId'] = configId
        sourceId = config['sourceId']
        matches_only_one_source(fs, sourceId)
        collection = db.config
        collection.create_index('configId', unique=True, sparse=True)
        # if not collection.find({'configId':configId}).count() > 0: # WARNING
        collection.insert_one(config)
        print(configId)

def ls(db, fs, args):
    collection = db.config
    cursor = collection.find()
    table = [[config['configId']] for config in cursor]
    print(tabulate.tabulate(table, headers=['configId'], tablefmt='plain'))

def show(db, fs, args):
    config = matches_only_one_config(db, args.configId)
    del config['_id']
    print(json.dumps(config, sort_keys=True, indent=1))

def rm(db, fs, args):
    config = matches_only_one_config(db, args.configId)
    configId = config['configId']
    # should rm run ref on config first!
    for run in db.run.find({'configId':configId}).limit(1):
        raise Exception('Found run referencing this configId=%s : runId=%s' % (configId, run['runId']))
    result = db.config.delete_one({'configId' : configId})
    print(configId)
