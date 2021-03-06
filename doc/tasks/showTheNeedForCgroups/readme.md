# We need cgroups to enforce isolation
## What is isolation and why do we need it?

Applications consume resources as they execute. Some application are better at increasing their resource consumption and can thus starve other applications. Isolation prevent this resource "stealing" from happening by setting absolute or relative limits on how much resources can be consummed by an application.

If performances scale linearly as a function of resources, you could argue:
- on one hand that resources are globaly well used and thus that isolation is unnecessary  but
- on the other hand you could argue that fairness between application is more important, or that the applications which are bad at increasing their resource consumption are more important and thus that isolation is necessary.

But performances don't always scale linearly as a function of resources which means that isolation is the only way to specify how you want the resources to be spent. Without isolation you might not get the best out of what you paid for.

# Experiments
## blkio cgroup
In this first set of experiments, where performances scale linearly as a function of disk bandwidth, I will show you that cgroups can prevent a greedy application from consumming more than another application.

### Setup
*A* and *B* are basicly the same. Except that *A* runs two threads in parallel to fetch the same amount of data from disk.

### Setup without Isolation
As we increase the total amount of disk bandwith, we can see that *A* always performs better than *B*.
![procAprocBWithoutBlkioIsolation](./blkio/data/procAprocBWithoutBlkioIsolation.png)
```
Performances
^
|        A 
|       /
|      / 
|     /
|    /
|   /    B
|  /  __/
| /__/
|//
+-----------> Total bandwidth
```

### Setup with Isolation
*A*'s and *B*'s bandwidth are both limited to half of the total bandwidth.
As we increase the total amount of disk bandwith, we can see that *A* and *B* always have the same performances.
![procAprocBWithBlkioIsolation](./blkio/data/procAprocBWithBlkioIsolation.png)
```
Performances
^
|             A B
|          _/
|        _/
|      _/
|    _/
|  _/
| /
+-----------> Total bandwidth
```

## memory cgroup
In this set of experiments, where performances do not scale linearly as a function of memory, I will show you that cgroups can obtain the same peak performances but with less total memory.

### Setup
*A* and *B* sequentially read from disk and have the same miss ratio (to try to avoid the disk bandwidth competition), but *A* has a very small but highly dynamic workingset where as *B* uses a huge static workingset.

### Setup without Isolation
In order to reach peak performances (defined by miss ratio and disk bandwidth), we need WA+WB+EXTRA amount of total memory.
![procAprocBWithoutMemoryIsolation](./memory/data/procAprocBWithoutMemoryIsolation.png)
```
Performances
^
|     A_____________________________________
|     /                               /.
|    /                               / . 
|   /                               /  . 
|  /                               /   .  
| /                               /    .
|/_______________________________/ B   . 
+--------------------------------------+----> Total memory
                                 ~WA+WB+EXTRA
```

### Setup with Isolation
In order to reach peak performances, we need WA+WB amount of total memory.
![procAprocBWithMemoryIsolation](./memory/data/procAprocBWithMemoryIsolation.png)
```
Performances
^
|     A________________
|     /            /.
|    /            / . 
|   /            /  . 
|  /            /   .  
| /            /    .
|/____________/ B   . 
+-------------------+--> Total memory
                 ~WA+WB
```
