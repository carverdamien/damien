import pymongo

def argparser(parser):
    parser = parser.add_parser('collector')
    parser.set_defaults(func=collect)

def collect(db, fs, args):
    import docker, threading
    def collect(db, clt, Id):
        try:
            db.dockercontainers.insert_one(clt.inspect_container(Id))
        except Exception as e:
            print(e)
        count = 0
        for stat in clt.stats(Id, decode=True):
            count += 1
            stat['Id'] = Id
            try:
                db.dockerstats.insert_one(stat)
            except Exception as e:
                print(e)
                print(stat)
            print(Id, count)
    def spawn_worker(Id):
            t = threading.Thread(target=collect, args=(db, clt, Id))
            t.daemon = True
            t.start()
    db.dockercontainers.create_index([('Id', pymongo.ASCENDING)], unique=True)
    db.dockerstats.create_index([('read', pymongo.ASCENDING), ('Id', pymongo.ASCENDING)], unique=True)
    clt = docker.Client()
    for container in clt.containers():
        spawn_worker(container['Id'])
    for event in clt.events(decode=True):
        print(event)
        if 'status' not in event:
            continue
        status = event['status']
        if status == 'start':
            spawn_worker(event['id'])
    pass
