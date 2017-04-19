# Setup A

* fix total memory 4G
* fix container memory 400MB (~10 containers max)
* fix total requests per sec
* fix churn rate: 10 per sec (~Toutes les secondes, il y a en moyenne 10 containers qui recoivent des requetes)

```
Response Time (95%)
^
|                ------------- Linux
|               /
|              /
|             /
|-------------
+------------|------------|--> nb container
0           10           20
```

```
Response Time (95%)
^
|              --------------- ACDC
|             /  
|-------------                
+------------|------------|--> nb container
0           10           20
```

La chute de perf depend du churn rate. Ne depend pas du nombre container.
FAUX: il a beaucoup de chance que ca depende du nombre de container et de distribition de la popularite des container.

Ce setup est inutile... On 


# Setup B

* fix total memory 4G
* fix container's memory 400MB
* fix 20 containers
* fix total requests per sec
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
