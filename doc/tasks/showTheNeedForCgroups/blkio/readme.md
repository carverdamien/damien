# 2 Cgroups
## Perf P1
![2CGperfP1][2CGperfP1]
## Perf P2
![2CGperfP2][2CGperfP2]

[2CGperfP1]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/doc/doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef/perf.png "2CGperfP1"
[2CGperfP2]: http://indium.rsr.lip6.fr:3000/carverdamien/damien/raw/doc/doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/3f71/perf.png "2CGperfP2"

# Memo
## Run
```
damien source add doc/tasks/showTheNeedForCgroups/blkio/source.py
damien config add doc/tasks/showTheNeedForCgroups/blkio/configSingleCgroup.json
damien run new 52faa270add75b2b01dc9f906178b6c327e613e04452594bad4ede89
damien config add doc/tasks/showTheNeedForCgroups/blkio/config2Cgroups.json
damien run new 2d8383eee5fd9421ada6da19f094d03a770a7fe377274e98efd5810d
```

## Generate images
```
DIR=doc/tasks/showTheNeedForCgroups/blkio/data/2Cgroups/06ef
./csv2img.py <(grep r $DIR/blkio.csv | cat <(echo 'x,y,label') -) $DIR/blkio.png
./csv2img.py <(grep -E '\.cache|\.limit|\.active_file|\.inactive_file' $DIR/memory.csv | cat <(echo 'x,y,label') -) $DIR/memory.png
./csv2img.py <(grep -E 'IO.*mb' $DIR/perf.csv | cat <(echo 'x,y,label') -) $DIR/perf.png
```
