#!/usr/bin/env python

_SOURCEID = 'af9584942cd1f24792326b05d44288af8eaf8395c9c3110ffc85ce0b'
_FILE_NAME = 'memory_of_containers_at_boot'

def open_file(fs):
    for _ in fs.find({'filename' : _FILE_NAME}):
        fs.delete(_._id)
    f = fs.new_file(filename=_FILE_NAME)
    print(f._id)
    return f

def do(db, fs):
    import pandas as pd
    import StringIO, csv, tempfile
    with tempfile.TemporaryFile() as tmp:
        writer = csv.writer(tmp)
        writer.writerow(['x', 'y', 'label'])
        for config in db.config.find({'sourceId' : _SOURCEID}):
            image = config['image']
            x = image.split(':')[0]
            configId = config['configId']
            for run in db.run.find({'configId' : configId, 'status' : 'done'}).limit(1):
                if 'files' not in run:
                    print('files not in', run)
                    continue
                for k,v in run['files'].iteritems():
                    data = fs.get(v).read()[:-1]
                    if len(data) == 0:
                        continue
                    df = pd.read_csv(StringIO.StringIO(data))
                    #print(df)
                    for label in ['usage_in_bytes', 'cache', 'rss']:
                        sel =  df['label'] == label+'/'+image
                        y = df[sel]['y'].mean()
                        writer.writerow([x,y,label])
        tmp.seek(0)
        f = open_file(fs)
        f.write(tmp.read())
        f.close()
        #print(fs.get(f._id).read()[:-1])
    
if __name__ == '__main__':
    import pymongo, gridfs
    clt = pymongo.MongoClient()
    db = clt['toto']
    fs = gridfs.GridFS(db)
do(db,fs)
