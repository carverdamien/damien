from lib.common import *
import json
import tabulate

def argparser(parser):
	parser = parser.add_parser('run')
	subparsers = parser.add_subparsers()
	#
	parser = subparsers.add_parser('ls')
	parser.set_defaults(func=ls)
	#
	parser = subparsers.add_parser('new')
	parser.set_defaults(func=new)
	parser.add_argument('configId', type=str)
	#
	parser = subparsers.add_parser('show')
	parser.set_defaults(func=show)
	parser.add_argument('runId', type=str)
	#
	parser = subparsers.add_parser('rm')
	parser.set_defaults(func=rm)
	parser.add_argument('runId', type=str)

def ls(db, fs, args):
    collection = db.run
    cursor = collection.find()
    table = [[run['runId'], run['status'], run['configId']] for run in cursor]
    print(tabulate.tabulate(table, headers=['runId', 'status', 'configId'], tablefmt="plain"))

def new(db, fs, args):
    config = matches_only_one_config(db, args.configId)
    run = { 'status' : 'created', 'configId' : config['configId'] }
    runId = db.run.insert_one(run).inserted_id
    db.run.update_one({'_id' : runId}, {"$set" : { 'runId' : str(runId) }})
    db.run.create_index('runId', unique=True, sparse=True)
    print(runId)

def show(db, fs, args):
    run = matches_only_one_run(db, args.runId)
    del run['_id']
    print(json.dumps(run, sort_keys=True, indent=1))

def rm(db, fs, args):
    run = matches_only_one_run(db, args.runId)
    runId = run['runId']
    fs.delete({'runId':runId})
    db.run.delete_one({'runId' : runId})
    print(runId)
