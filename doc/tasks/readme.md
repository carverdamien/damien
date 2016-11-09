# Tasks

## Show that consolidation works when we don't need cgroups.
Choose A and B such that there is no need for cgroups.
Run A and B. Pause B. Start C.
- [x] using filebench and malloc, show that C can reclaim B's memory. summarised [here](./showThatConsolidation/works), detailed [here](http://indium.rsr.lip6.fr/run/581a2a7d5369e14e17707a35)

## Show the need for cgroups.
Choose A and B such that there is a need for cgroups.
Run A and B in same cgroup and compare with A and B running in different cgroups.

### Show the need for blkio cgroup
- [x] using filebench. summarised [here](./showTheNeedForCgroups/blkio), detailed [here](http://indium.rsr.lip6.fr/run/5811fe3e5369e17479a138a3,5811fe3f5369e1748dab89d3), without local limits detailed [here](http://indium.rsr.lip6.fr/run/58234dcd5369e136533c1fe2)
- [ ] using sysbench.

### Show the need for memory cgroup
- [x] using filebench. summarised [here](./showTheNeedForCgroups/memory), detailed [here](http://indium.rsr.lip6.fr/run/58137f045369e1372bb922d5,58137f055369e1373d0d6023)
- [ ] using sysbench.

## Show that consolidation does not works when we need/use cgroups.
Run A and B. Pause B. Start C.
- [x] using filebench and malloc, show that C cannot reclaim B's memory. summarised [here](./showThatConsolidation/doesnotwork/withFilebench), detailed [here](http://indium.rsr.lip6.fr/run/581a2a445369e14db265b07f)
- [x] using sysbench and cassandra, show that C cannot reclaim B's memory. summarised [here](./showThatConsolidation/doesnotwork/withSysbench), detailed [here](http://indium.rsr.lip6.fr/run/581c91c55369e121413dd80b)

## Show that we can fix this with little overhead
check [this](http://indium.rsr.lip6.fr/run/58210dbb5369e10f484a92d1)
- [ ] Show that we can detect that A is active and B is inactive
- [ ] Show that we can protect A

## Performance/Resource tunning
- [ ] for any application, show performance as function of resource
