#!/bin/bash
set -e -x
source .activate-completion.sh
DURATION=60
SOURCE=$(damien source add series/boot/source.py)
cat_config(){
cat <<EOF
{
"sourceId" : "$SOURCE",
    "duration" : $DURATION,
    "image" : "$IMAGE:latest"
}
EOF
}
cat series/boot/list | while read IMAGE; do damien config add <(cat_config) | xargs damien run new; done
