# Patch
Use `dpgin/dt >= dpgout/dt` as a detector.
* OK: It will still make mistakes
* BUT: It will fix it faster
* AT: low cost

Use timestamps to date the last reclaim.
If all memcg are detected as active, then reclaim to the Least Recently Reclaimed, because if it is realy active then it had plenty of time to protect its pages.
* OK: It can still make mistakes
* BUT: It reduces the chances of making mistakes
* AT: low cost
# Very Stupid Patch
```
+---------------+---------------+
| dpgout/dt = 0 | dpgout/dt > 0 |
+---------------+---------------+
|    reclaim    |  do nothing   |
+---------------+---------------+
```
# Stupid Patch
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
