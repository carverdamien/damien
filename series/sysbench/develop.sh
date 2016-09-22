#!/bin/bash
set -e -x
DBNAME=sysbench
echo mongo<<EOF
use ${DBNAME}
db.dropDatabase()
EOF
damien() { ./damien --dbname ${DBNAME} $@; }
SOURCEID=$( damien source add ./series/${DBNAME}/source.py)
cat_config() {
cat <<EOF
{ "sourceId" : "${SOURCEID}" }
EOF
}
damien run new $(damien config add <(cat_config))
damien daemon || true
damien httpd || true
