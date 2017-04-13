#include "master.h"

void* masterFunction(void *args) {
	struct master *master = args;
	struct config* config = master->config;
	int i = 0;
	struct int_dist* interarrival_dist = config->interarrival_dist;
	while(1) {
	  struct worker *worker = config->workers[i];

	  // Round robin load
	  i = (i + 1) % config->n_workers;
	  
	  if (interarrival_dist) {
	    if (worker->interarrival_time <= 0) {
	      worker->interarrival_time = getIntQuantile(interarrival_dist); //In microseconds
	    } else {
	      continue;
	    }
	  }

	  worker_add_load(worker, 1);
	}
	return NULL;
}

void createMaster(struct config* config) {
	config->master = malloc(sizeof(struct master));
	config->master->config = config;
	if (pthread_create(&config->master->thread, NULL, masterFunction, config->master))
		printf("Error creating master\n");
}
