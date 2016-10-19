set $dir=/data/inmemory
set $filesize=1g
set $iosize=1m
set $nthreads=100

define file name=data,path=$dir,size=$filesize,reuse,prealloc

define process name=seqreader,instances=1
{
  thread name=seqreaderthread,memsize=1m,instances=$nthreads
  {
    flowop read name=read,filename=data,iosize=$iosize,directio=0,fd=1
    flowop eventlimit name=eventlimit
  }
}
