#ifndef MASTER_H
#define MASTER_H

#include <pthread.h>
#include "config.h"
#include "worker.h"

struct master {
	struct config* config;
	pthread_t thread;
};

void createMaster(struct config* config);

#endif
