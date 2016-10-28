set $dir=/data/outmemory
set $iosize=1m

define file name=coldfile1,path=$dir/files,size=5g,reuse,prealloc
define file name=coldfile2,path=$dir/files,size=5g,reuse,prealloc

# 16 hit for 2 miss

define process name=p2-a1,instances=1
{
thread name=access1, memsize=1m, instances=1
{
flowop semblock name=semblock1, value=1, highwater=1
flowop read name=readfile1,fd=1,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost1, target=semblock1done, value=1
flowop sempost name=sempost1, target=semblock2, value=1
}
}
define process name=p2-a2,instances=1
{
thread name=access2, memsize=1m, instances=1
{
flowop semblock name=semblock2, value=1, highwater=1
flowop read name=readfile2,fd=2,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost2, target=semblock3, value=1
}
}
define process name=p2-a3,instances=1
{
thread name=access3, memsize=1m, instances=1
{
flowop semblock name=semblock3, value=1, highwater=1
flowop read name=readfile3,fd=3,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost3, target=semblock4, value=1
}
}
define process name=p2-a4,instances=1
{
thread name=access4, memsize=1m, instances=1
{
flowop semblock name=semblock4, value=1, highwater=1
flowop read name=readfile4,fd=4,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost4, target=semblock5, value=1
}
}
define process name=p2-a5,instances=1
{
thread name=access5, memsize=1m, instances=1
{
flowop semblock name=semblock5, value=1, highwater=1
flowop read name=readfile5,fd=5,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost5, target=semblock6, value=1
}
}
define process name=p2-a6,instances=1
{
thread name=access6, memsize=1m, instances=1
{
flowop semblock name=semblock6, value=1, highwater=1
flowop read name=readfile6,fd=6,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost6, target=semblock7, value=1
}
}
define process name=p2-a7,instances=1
{
thread name=access7, memsize=1m, instances=1
{
flowop semblock name=semblock7, value=1, highwater=1
flowop read name=readfile7,fd=7,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost7, target=semblock8, value=1
}
}
define process name=p2-a8,instances=1
{
thread name=access8, memsize=1m, instances=1
{
flowop semblock name=semblock8, value=1, highwater=1
flowop read name=readfile8,fd=8,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost8, target=semblock9, value=1
}
}
define process name=p2-a9,instances=1
{
thread name=access9, memsize=1m, instances=1
{
flowop semblock name=semblock9, value=1, highwater=1
flowop read name=readfile9,fd=9,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost9, target=semblock10, value=1
}
}
define process name=p2-a10,instances=1
{
thread name=access10, memsize=1m, instances=1
{
flowop semblock name=semblock10, value=1, highwater=1
flowop read name=readfile10,fd=10,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost10, target=semblock11, value=1
}
}
define process name=p2-a11,instances=1
{
thread name=access11, memsize=1m, instances=1
{
flowop semblock name=semblock11, value=1, highwater=1
flowop read name=readfile11,fd=11,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost11, target=semblock12, value=1
}
}
define process name=p2-a12,instances=1
{
thread name=access12, memsize=1m, instances=1
{
flowop semblock name=semblock12, value=1, highwater=1
flowop read name=readfile12,fd=12,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost12, target=semblock13, value=1
}
}
define process name=p2-a13,instances=1
{
thread name=access13, memsize=1m, instances=1
{
flowop semblock name=semblock13, value=1, highwater=1
flowop read name=readfile13,fd=13,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost13, target=semblock14, value=1
}
}
define process name=p2-a14,instances=1
{
thread name=access14, memsize=1m, instances=1
{
flowop semblock name=semblock14, value=1, highwater=1
flowop read name=readfile14,fd=14,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost14, target=semblock15, value=1
}
}
define process name=p2-a15,instances=1
{
thread name=access15, memsize=1m, instances=1
{
flowop semblock name=semblock15, value=1, highwater=1
flowop read name=readfile15,fd=15,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost15, target=semblock16, value=1
}
}
define process name=p2-a16,instances=1
{
thread name=access16, memsize=1m, instances=1
{
flowop semblock name=semblock16, value=1, highwater=1
flowop read name=readfile16,fd=16,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost16, target=semblock17, value=1
}
}
define process name=p2-a17,instances=1
{
thread name=access17, memsize=1m, instances=1
{
flowop semblock name=semblock17, value=1, highwater=1
flowop read name=readfile17,fd=17,iosize=$iosize,filename=coldfile1
flowop sempost name=sempost17, target=semblock18, value=1
}
}
define process name=p2-aT,instances=1
{
thread name=thrashAccess, memsize=1m, instances=1
{
flowop sempost name=thrashsempost, target=semblock1, value=1
flowop semblock name=semblock1done, value=1, highwater=1
flowop read name=trash, filename=coldfile2, iosize=$iosize, fd=18
flowop semblock name=semblock18, value=1, highwater=1
}
}
