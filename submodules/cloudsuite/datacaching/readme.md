# Benchmark d'Evaluation 

Nous disposons deja d'un microbenchmark pour montrer notre probleme. (Le demarrage d'un conteneur perturbe les conteneurs actifs).
On souhaite maintenant concevoir un benchmark pour evaluer notre solution.
L'isolation des ressources permet d'offrir des garanties de performance tandis que la consolidation permet d'economiser des ressources.
L'ideal est donc produire un graph de ce type:

```
Isolation
^
|
|
+-----> Consolidation
```

Ce graph montrera qu'avec Linux plus on consolide, plus on perd d'isolation, alors que dans les memes conditions, ACDC offre plus d'isolation.

# Workload

Nous ne disposons pas de traces pertinentes issues de l'industrie.
Nous proposons d'utiliser le principe de pareto comme modele.

Dans notre workload, on pourra dire que 80% des requetes recus par une machine ne sont destinees qu'a 20% des conteneurs (80-20 parametrable).
Il y a donc 80% des conteneurs qui utilisent peu leurs ressources. Ces ressources peuvent donc etre consolidees.


```
Temps de Reponse (90% percentile)
^
|              Linux       ACDC
|                 /       _/
|                /      _/
|               /     _/
|              /    _/
|             /   _/
|            /  _/
|           / _/
|          /_/
|         //
|       _/
|     _/
|   _/
| _/              
|/                
+-------|-------|-------|-------|-------> Memoire en moins
0%     20%     40%     60%     80%
```
