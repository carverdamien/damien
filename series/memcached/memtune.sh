#!/bin/bash

memory() {
python <<EOF
import json
m=2.5*2**30
min  = 2304357323 
max  = 2304464697
step = 4 * 2**10
for i in range(int(min),int(max+1),int(step)): print(i)
EOF
}

config() {
python <<EOF
import json
config = json.load(open('memtune.json'))
config['containers'][1]['host_config']['mem_limit'] = $1
print(json.dumps(config))
EOF
}

damien --dbname prod analytics --name memtuneMemcached new
damien --dbname prod analytics --name memtuneMemcached view ops_s view.py
for m in $(memory)
do
    RUN_ID=$(damien --dbname prod config add <(config $m) | xargs damien --dbname prod run new) &&
    damien --dbname prod analytics --name memtuneMemcached data "${RUN_ID}"
done
