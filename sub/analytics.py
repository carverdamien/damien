import tabulate
import json

def argparser(parser):
    parser = parser.add_parser('analytics')
    parser.add_argument('--name', type=str)
    subparsers = parser.add_subparsers()
    #
    parser = subparsers.add_parser('new')
    parser.set_defaults(func=new)
    #
    parser = subparsers.add_parser('show')
    parser.set_defaults(func=show)
    #
    parser = subparsers.add_parser('data')
    parser.set_defaults(func=data)
    parser.add_argument('dataref', type=str)
    #
    parser = subparsers.add_parser('view')
    parser.set_defaults(func=view)
    parser.add_argument('view', type=str)
    parser.add_argument('view_py', type=str)
    #
    parser = subparsers.add_parser('rm')
    parser.set_defaults(func=rm)

def new(db, fs, args):
    analytics = {'name' : args.name, 'dataref': [], 'view' : {}}
    collection = db.analytics
    collection.create_index('name', unique=True, sparse=True)
    collection.insert_one(analytics)
    print(args.name)

def show(db, fs, args):
    analytics = next(db.analytics.find({'name' : args.name}, {'_id':0}))
    print(json.dumps(analytics, sort_keys=True, indent=1))

def data(db, fs, args):
    print(db.analytics.update_one({'name':args.name}, {'$push':{'dataref':args.dataref}}))

def view(db, fs, args):
    print(db.analytics.update_one({'name':args.name}, {'$set':{'view.%s' % args.view : open(args.view_py).read()}}))

def rm(db, fs, args):
    name =  args.name
    result = db.analytics.delete_one({'name' : name})
    print(name)
