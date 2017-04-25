import json, influxdb, sys, datetime

host = sys.argv[1]
port = sys.argv[2]
user = sys.argv[3]
pwrd = sys.argv[4]
name = sys.argv[5]

client = influxdb.InfluxDBClient(host, port, user, pwrd, name)
client.create_database(name)

for line in sys.stdin:
    try:
        json_body = json.loads(line)
        time = datetime.datetime.utcfromtimestamp(json_body['time'])
        del json_body['time']
        json_body = [
            {
                "measurement": "application_metrics",
                "tags": {},
                "time": time,
                "fields": json_body
            }
        ]
        client.write_points(json_body)
    except Exception as e:
        print(line)
        print(e)

