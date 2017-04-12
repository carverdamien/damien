#include "master.h"

void* masterFunction(void *args) {
	struct master *master = args;
	struct config* config = master->config;
	while(1) {
		int i;
		for(i = 0; i < config->n_workers; i++) {
			worker_add_load(config->workers[i], 100);
		}
		sleep(1);
	}
	return NULL;
}

void createMaster(struct config* config) {
	config->master = malloc(sizeof(struct master));
	config->master->config = config;
	if (pthread_create(&config->master->thread, NULL, masterFunction, config->master))
		printf("Error creating master\n");
}
