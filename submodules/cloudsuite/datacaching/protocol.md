# Setup A
* total memory 4G
* container's memory 400MB
* fix churn rate 0.1/sec
```
Perf
^
|-------------
|             \
|              \
|               \
|                ------------- Linux
+------------|------|-----|--> nb container
0           10     100   1000
```
```
Perf
^
|-------------
|             \
|              --------------- ACDC
|               
|                
+------------|------|-----|--> nb container
0           10     100   1000
```
La chute de perf depend du churn rate. Ne depend pas du nombre container.

# Setup B
* total memory 4G
* container's memory 400MB
* fix 1000 containers
* Chute = Perf(10containers) - Perf(1000containers)
```
Chute
^            LINUX
|             /
|            /
|           /
|          /
|         /
|        /
|       /
|      /
|     /
|    /
|   /
|  /
| /              
|/                
+-----|------|------|-----|--> Churn Rate
0    0.1    10     100   1000
```
```
Chute
^                          ACDC
|                         _/
|                       _/
|                     _/
|                   _/
|                 _/
|               _/
|             _/
|           _/
|         _/
|       _/
|     _/
|   _/
| _/              
|/                
+-----|------|------|-----|--> Churn Rate
0    0.1    10     100   1000
```
La perte global scale en fonction du churn rate
