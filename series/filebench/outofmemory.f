set $dir=/data/outofmemory

define fileset name=bigfileset,path=$dir,size=1g,entries=4,dirwidth=20,prealloc=100,reuse
define fileset name=flushfileset,path=$dir,size=1g,entries=1,dirwidth=2,prealloc=100,reuse

define process name=flusher,instances=1
{
  thread name=flusherthread,memsize=1m,instances=1
  {
    flowop openfile name=openfile2,filesetname=flushfileset,fd=2
    flowop readwholefile name=flush,iosize=1m,directio=0,fd=2,iters=100
    flowop closefile name=closefile2,fd=2
    flowop wakeup name=mywakeup,target=myblock
    #flowop block name=blockforever
  }
  thread name=thrashthread,memsize=1m,instances=99
  {
    flowop block name=myblock
    flowop openfile name=openfile1,filesetname=bigfileset,fd=1
    flowop read name=readfile1,fd=1,iosize=1m,iters=2048
    flowop closefile name=closefile1,fd=1
    flowop wakeup name=mywakeup,target=myblock
  }
}
