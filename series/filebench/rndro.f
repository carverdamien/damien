set $dir=/data/rndro
set $hotfilesize=1g
set $coldfilesize=4g
set $hotiosize=1m
set $coldiosize=1m
set $nthreads=100

define file name=hotfile,path=$dir,size=$hotfilesize,reuse,prealloc
define file name=coldfile,path=$dir,size=$coldfilesize,reuse,prealloc

define process name=rndreader,instances=1
{
  thread name=rndreaderthread,memsize=1m,instances=$nthreads
  {
    flowop read name=readhot,filename=hotfile,iosize=$hotiosize,random,workingset=0,directio=0,fd=1,iters=64
    flowop read name=readcold,filename=coldfile,iosize=$coldiosize,random,workingset=0,directio=0,fd=2
  }
}
