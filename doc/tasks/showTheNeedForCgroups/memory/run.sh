# SOURCE ME!

damien --dbname prod source add source.py
config_generator() { python config.py $ARGS; }
schedule_runs() {
    damien --dbname prod analytics --name ${ANALYTICS} new
    for i in $(seq $(config_generator | wc -l))
    do
	RUN_ID=$(damien --dbname prod run new $(damien --dbname prod config add <(config_generator | head -n $i | tail -n 1)))
	damien --dbname prod analytics --name ${ANALYTICS} data "${RUN_ID}"
    done
}

ARGS='--isolation=yes'
ANALYTICS=procAprocBWithMemoryIsolation
schedule_runs
ARGS='--isolation=no'
ANALYTICS=procAprocBWithoutMemoryIsolation
schedule_runs
