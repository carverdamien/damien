#include "master.h"

void* masterFunction(void *args) {
	struct master *master = args;
	struct config* config = master->config;
	int i = 0;
	struct timeval last_write_time;
	double diff;
	int interarrival_time = 0;
	struct int_dist* interarrival_dist = config->interarrival_dist;
	gettimeofday(&last_write_time, NULL);
	while(1) {
	  struct timeval timestamp, timediff, timeadd;

	  gettimeofday(&timestamp, NULL);
	  timersub(&timestamp, &last_write_time, &timediff);
	  diff = timediff.tv_usec * 1e-6  + timediff.tv_sec;
	  
	  if (interarrival_dist) {
	    if (interarrival_time <= 0) {
	      interarrival_time = getIntQuantile(interarrival_dist); //In microseconds
	    }

	    if (interarrival_time/1.0e6 > diff)
	      continue;
	  }

	  timeadd.tv_sec = 0; timeadd.tv_usec = interarrival_time; 
	  interarrival_time = -1;
	  timeradd(&last_write_time, &timeadd, &last_write_time);
	  
	  // Round robin load
	  worker_add_load(config->workers[i], 1);
	  i = (i + 1) % config->n_workers;
	}
	return NULL;
}

void createMaster(struct config* config) {
	config->master = malloc(sizeof(struct master));
	config->master->config = config;
	if (pthread_create(&config->master->thread, NULL, masterFunction, config->master))
		printf("Error creating master\n");
}
