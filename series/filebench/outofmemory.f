set $dir=/data/outmemory
set $iosize=1m
set $thrash=2

define file name=hotfile,path=$dir,size=512m,reuse,prealloc
define file name=coldfile1,path=$dir,size=5g,reuse,prealloc
define file name=coldfile2,path=$dir,size=5g,reuse,prealloc

# One hit for 2 parallel miss

define process name=process2, instances=1
{
  thread name=HotThread, memsize=1m, instances=1
  {
    flowop semblock name=hotsemblock, value=$thrash, highwater=1
    flowop read name=hot, filename=hotfile, iosize=$iosize, fd=1
    flowop sempost name=hotsempost, target=hotsemblockdone, value=$thrash
  }
  thread name=ColdThread1, memsize=1m, instances=1
  {
    flowop read name=cold1, filename=coldfile1, iosize=$iosize, fd=2
    flowop sempost name=coldsempost, target=hotsemblock, value=1
    flowop semblock name=hotsemblockdone, value=1, highwater=1
  }
  thread name=ColdThread2, memsize=1m, instances=1
  {
    flowop read name=cold2, filename=coldfile2, iosize=$iosize, fd=3
    flowop sempost name=coldsempost, target=hotsemblock, value=1
    flowop semblock name=hotsemblockdone, value=1, highwater=1
  }
}
