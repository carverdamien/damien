# Run
```
damien source add doc/tasks/showTheNeedForCgroups/blkio/source.py
damien config add doc/tasks/showTheNeedForCgroups/blkio/configSingleCgroup.json
damien run new 52faa270add75b2b01dc9f906178b6c327e613e04452594bad4ede89
damien config add doc/tasks/showTheNeedForCgroups/blkio/config2Cgroups.json
damien run new 2d8383eee5fd9421ada6da19f094d03a770a7fe377274e98efd5810d
```

```
./csv2img.py <(grep r doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/blkio.csv | cat <(echo 'x,y,label') -) doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/blkio.png
./csv2img.py <(grep -E '\.cache|\.limit|\.active_file|\.inactive_file' doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/memory.csv | cat <(echo 'x,y,label') -) doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/memory.png
./csv2img.py <(grep -E 'IO.*mb' doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/perf.csv | cat <(echo 'x,y,label') -) doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/perf.png
```

# 2 Cgroups
P1:
![blkioP1][blkioP1]
![memoryP1][memoryP1]
![perfP1][perfP1]

[blkioP1]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/doc/doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/blkio.png "blkioP1"
[memoryP1]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/doc/doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/memory.png "memoryP1"
[perfP1]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/doc/doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/perf.png "perfP1"
