set $dir=/data/outofmemory
set $hotfilesize=1g
set $coldfilesize=4g
set $hotiosize=1m
set $coldiosize=1m
set $nthreads=100

define file name=hotfile,path=$dir,size=$hotfilesize,reuse,prealloc
define file name=coldfile,path=$dir,size=$coldfilesize,reuse,prealloc

define process name=seqreader,instances=1
{
  thread name=seqreaderthread,memsize=1m,instances=$nthreads
  {
    flowop read name=readhot,filename=hotfile,iosize=$hotiosize,directio=0,fd=1,iters=2
    flowop read name=readcold,filename=coldfile,iosize=$coldiosize,directio=0,fd=2
  }
}
