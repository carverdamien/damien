# 2 Cgroups
![2CGperf][2CGperf]
[2CGperf]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/master/doc/tasks/showTheNeedForCgroups/memory/data/2Cgroups/perf.png "2CGperf"

# 1 Cgroup
![1CGperf][1CGperf]
[1CGperf]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/master/doc/tasks/showTheNeedForCgroups/memory/data/SingleCgroup/perf.png "1CGperf"

# Memo
## Generate perfs plot
```
./csv2img.py <(grep -E 'IO.*mb' <(cat doc/tasks/showTheNeedForCgroups/memory/data/2Cgroups/*/perf.csv) | cat <(echo 'x,y,label') -) doc/tasks/showTheNeedForCgroups/memory/data/2Cgroups/perf.png
./csv2img.py <(grep -E 'IO.*mb' <(cat doc/tasks/showTheNeedForCgroups/memory/data/SingleCgroup/*/perf.csv) | cat <(echo 'x,y,label') -) doc/tasks/showTheNeedForCgroups/memory/data/SingleCgroup/perf.png
```
