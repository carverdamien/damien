![perf](./perf.png)
```
../../../../csv2img.py <(grep -E 'IO.*mb' <(cat data/*/perf.csv) | cat <(echo 'x,y,label') -) perf.png
```