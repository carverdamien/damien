def matches_only_one_file(fs, type, field, regex):
    cursor = fs.find({'type' : type, field : {'$regex':regex}})
    count = 0
    for f in cursor:
        if count == 1:
            raise Exception('More than one match!')
        count += 1
    if count == 0:
        raise Exception('No match')
    return f

def matches_only_one_source(fs, regex):
    return matches_only_one_file(fs, 'source', 'sourceId', regex)

def matches_only_one(collection, field, regex):
    cursor = collection.find({field: {'$regex':regex}})
    count = 0
    for doc in cursor:
        if count == 1:
            raise Exception('More than one match!')
        count += 1
    if count == 0:
        raise Exception('No match')
    return doc

def matches_only_one_config(db, regex):
    return matches_only_one(db.config, 'configId', regex)

def matches_only_one_run(db, regex):
    return matches_only_one(db.run, 'runId', regex)