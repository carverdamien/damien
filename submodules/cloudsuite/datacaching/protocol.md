# Setup A

* fix total memory 4G
* fix container memory 400MB (~10 containers max)
* fix churn rate 10/sec. (Toutes les secondes, il y a au plus 10 containers qui recoivent des requetes)

```
Perf
^
|-------------
|             \
|              \
|               \
|                ------------- Linux
+------------|------------|--> nb container
0           10           20
```

```
Perf
^
|-------------
|             \
|              --------------- ACDC
|               
|                
+------------|------------|--> nb container
0           10           20
```

La chute de perf depend du churn rate. Ne depend pas du nombre container.

# Setup B

* fix total memory 4G
* fix container's memory 400MB
* fix 20 containers
* Loss = Perf(10containers) - Perf(20containers) (Ce que l'on perd en faisant de l'overcommit)

```
Loss
^                  Linux
|                  /
|                 /
|                /
|               /
|              /
|             /
|            /
|           /
|         _/
|       _/  
|     _/    
|   _/      
| _/              
|/                
+-----|-----|-----|-----|--> Churn Rate
0     5     10    15    20
```

```
Loss
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
+-----|-----|-----|-----|--> Churn Rate
0     5     10    15    20
```

La perte global scale en fonction du churn rate.
