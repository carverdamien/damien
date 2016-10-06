from lib.common import *
import hashlib
import tabulate

def argparser(parser):
	parser = parser.add_parser('source')
	subparsers = parser.add_subparsers()
	#
	parser = subparsers.add_parser('add')
	parser.set_defaults(func=add)
	parser.add_argument('py_file', type=str)
	#
	parser = subparsers.add_parser('ls')
	parser.set_defaults(func=ls)
	#
	parser = subparsers.add_parser('show')
	parser.set_defaults(func=show)
	parser.add_argument('sourceId')
	#
	parser = subparsers.add_parser('rm')
	parser.set_defaults(func=rm)
	parser.add_argument('sourceId')

def add(db, fs, args):
    with open(args.py_file) as py_file:
        source = py_file.read()
        sourceId = hashlib.sha224(source).hexdigest()
        if not fs.exists({'type':'source', 'sourceId':sourceId}):
            fs.put(source, type='source', sourceId=sourceId, filename=args.py_file)
        print(sourceId) 

def ls(db, fs, args):
    cursor = fs.find({'type':'source'})
    table = [[source.name, source.sourceId] for source in cursor]
    print(tabulate.tabulate(table, headers=['name', 'sourceId'], tablefmt='plain'))

def show(db, fs, args):
    f = matches_only_one_source(fs, args.sourceId)
    print(f.read()[:-1])

def rm(db, fs, args):
    f = matches_only_one_source(fs, args.sourceId)
    sourceId = f.sourceId
    # delete config ref on source first!
    for config in db.config.find({'sourceId':sourceId}).limit(1):
        raise Exception('Found config referencing this sourceId=%s : configId=%s' % (sourceId, config['configId']))
    fs.delete(f._id)
    print(sourceId)