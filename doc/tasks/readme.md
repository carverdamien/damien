# Tasks

## Show that consolidation works when we don't need cgroups.
Choose A and B such that there is no need for cgroups.
Run A and B. Pause B. Start C.
- [ ] using filebench and malloc, show that C can reclaim B's memory.

## Show the need for cgroups.
Choose A and B such that there is a need for cgroups.
Run A and B in same cgroup and compare with A and B running in different cgroups.

### Show the need for blkio cgroup
- [ ] using filebench.
- [ ] using sysbench.

### Show the need for memory cgroup
- [ ] using filebench.
- [ ] using sysbench.

## Show that consolidation does not works when we need/use cgroups.
Run A and B. Pause B. Start C.
- [ ] using filebench and malloc, show that C cannot reclaim B's memory.
- [ ] using sysbench and cassandra, show that C cannot reclaim B's memory.
