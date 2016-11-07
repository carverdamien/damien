# Patch
```
+---------------+---------------+
| dpgout/dt = 0 | dpgout/dt > 0 |
+---------------+---------------+
|    reclaim    |  do nothing   |
+---------------+---------------+
```
# Patch
```
+-------------------------------+-----------------------------------------------+
|         dpgout/dt = 0         |                 dpgout/dt > 0                 |
+---------------+---------------+---------------+-------------------------------+
| dpgact/dt = 0 | dpgact/dt > 0 | dpg_in/dt = 0 |         dpg_in/dt > 0         |
+---------------+---------------+---------------+---------------+---------------+
|    reclaim    |   scan_only   |    reclaim    | dpgact/dt = 0 | dpgact/dt > 0 |
+---------------+---------------+---------------+---------------+---------------+
                                                |    reclaim    |   scan_only   |
                                                +---------------+---------------+
```
Metric Test     | Meanning
----------------|--------------------------------------------------------
`dpgout/dt = 0` | no page was evicted out of memory since last reclaim
`dpgout/dt > 0` | some pages were evicted out of memory since last reclaim
`dpg_in/dt = 0` | no page was loaded in memory since last reclaim
`dpg_in/dt > 0` | some pages were loaded in memory since last reclaim
`dpgact/dt = 0` | no page was activated since last reclaim
`dpgact/dt > 0` | some pages were activated since last reclaim
