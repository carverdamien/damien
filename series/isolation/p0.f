set $dir=/data/p0
set $cached=true
set $sleep=0
set $hotfilesize=536870912
set $coldfilesize=1073741824
set $iosize=1m
set $nthreads=100

define file name=hotfile,path=$dir,size=$hotfilesize,prealloc,reuse,cached=$cached
define file name=coldfile,path=$dir,size=$coldfilesize,prealloc,reuse,cached=$cached

define process name=filereader,instances=1
{
  thread name=filereaderthread,memsize=1m,instances=$nthreads
  {
    flowop readwholefile name=sr0-hot,filename=hotfile,iosize=$iosize
    flowop delay name=s-0,value=$sleep
    flowop readwholefile name=sr1-hot,filename=hotfile,iosize=$iosize
    flowop delay name=s-1,value=$sleep
    flowop readwholefile name=sr-cold,filename=coldfile,iosize=$iosize
    flowop delay name=s-2,value=$sleep
  }
}
