set $dir=/data/inmemory
set $filesize=1g
set $iosize=512k
set $nthreads=1

define file name=data,path=$dir,size=$filesize,reuse,prealloc

define process name=imreader,instances=1
{
  thread name=imthread,memsize=100m,instances=$nthreads
  {
    flowop read name=read,filename=data,iosize=$iosize,directio=0,fd=1,iters=1
  }
}
