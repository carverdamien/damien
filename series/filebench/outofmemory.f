set $dir=/data/outmemory
set $iosize=1m

define fileset name=coldfile1,path=$dir/filesets,size=5g,reuse,prealloc,entries=1,dirwidth=1
define file name=coldfile2,path=$dir/files,size=5g,reuse,prealloc

# One hit for 2 miss

define process name=process2,instances=1
{
thread name=firstAccess, memsize=1m, instances=1
{
flowop semblock name=firstsemblock, value=1, highwater=1
flowop read name=first, filesetname=coldfile1, iosize=$iosize, fd=1
flowop sempost name=firstsempost, target=firstsemblockdone, value=1
}
thread name=secondAccess, memsize=1m, instances=1
{
flowop semblock name=secondsemblock, value=1, highwater=1
flowop read name=second, filesetname=coldfile1, iosize=$iosize, fd=2
flowop sempost name=secondsempost, target=secondsemblockdone, value=1
}
thread name=thrashAccess, memsize=1m, instances=1
{
flowop sempost name=thrashsempost, target=firstsemblock, value=1
flowop semblock name=firstsemblockdone, value=1, highwater=1
flowop read name=trash, filename=coldfile2, iosize=$iosize, fd=3
flowop sempost name=thrashsempost, target=secondsemblock, value=1
flowop semblock name=secondsemblockdone, value=1, highwater=1
}
}
