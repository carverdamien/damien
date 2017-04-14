#ifndef WORKER_H
#define WORKER_H

#include <pthread.h>
#include <malloc.h>
#include <event2/event.h>
#include <sys/time.h>
#include <errno.h>
#include "config.h"
#include "conn.h"
#include "request.h"
#include "response.h"
#include "generate.h"

#include "mt19937p.h"

struct worker {
  
  struct config* config;

  pthread_t thread;
  struct event_base* event_base;
  struct conn** connections;
  int nConnections;
  int cpu_num;
  struct timeval last_write_time;
  int interarrival_time;
  unsigned long load_requested;
  unsigned long load_generated;
  pthread_cond_t load_requested_cond;
  pthread_mutex_t load_requested_lock;

  int n_requests;
  int current_request_id;

  struct mt19937p myMT19937p;
  int warmup_key;
  int warmup_key_check;	
  int received_warmup_keys;

};


void sendCallback(int fd, short eventType, void* args);
void receiveCallback(int fd, short eventType, void* args);
void* workerFunction(void* arg);
void workerLoop(struct worker* worker);
void createWorkers(struct config* config);
struct worker* createWorker(struct config* config, int cpuNum);
void worker_add_load(struct worker* worker, unsigned long load);

#endif
