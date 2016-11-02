# Perf
![perf](./perf.png)

# Memory
![memory](./memory.png)

# Memo
```
../../../../csv2img.py <(grep -E 'IO.*mb' <(cat data/*/perf.csv) | cat <(echo 'x,y,label') -) perf.png
../../../../csv2img.py <(grep -E '\.stats\.cache|\.stats\.rss' <(cat data/*/memory.csv) | cat <(echo 'x,y,label') -) memory.png
```
