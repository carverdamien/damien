import sys
import json

config = json.load(open(sys.argv[1]))
total_time = int(sys.argv[2])
quantum = int(sys.argv[3])
warm_up = 30

if quantum > 0:
    assert(total_time % quantum == 0)
    schedules = [
        [[0,         warm_up], [2*warm_up, total_time]],
        [[warm_up,   warm_up], [warm_up,      quantum]] + [[quantum,quantum]]*(total_time/2/quantum - 1),
        [[2*warm_up, warm_up], [quantum,      quantum]] + [[quantum,quantum]]*(total_time/2/quantum - 1),
    ]
else:
    schedules = [
        [[0,         warm_up], [2*warm_up, total_time]],
        [[warm_up,   warm_up], [warm_up,   total_time]],
        [[2*warm_up, warm_up], [quantum,   total_time]],
    ]
    
for i in range(3):
    config['memtier_ctl'][i]['schedule'] = schedules[i]
print(json.dumps(config))
