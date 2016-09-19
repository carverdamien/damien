#!/bin/bash
set -x
for link in https://hub.docker.com/explore/?page={1..100}
do
    curl -s $link | indent - -o - 2>/dev/null | sed -n 's/.*"\/_\/\([a-z\-]*\)\/" data.*/\1/p'
    sleep 1
done 
