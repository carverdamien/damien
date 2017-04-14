
#ifndef CONN_H
#define CONN_H


#define MEMCACHED_PORT 11211

#include <net/if.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <malloc.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "config.h"

#define QUEUE_SIZE 10000
#define INCR_FIX_QUEUE_SIZE 100

struct conn {
  int sock;
  int port;	
  int uid;
  int protocol;
  struct worker *worker;
  int server;
  //Circular queues
  struct request* request_queue[QUEUE_SIZE];
  int request_queue_head;
  int request_queue_tail;
  struct request* incr_fix_queue[INCR_FIX_QUEUE_SIZE];
  int incr_fix_queue_head;
  int incr_fix_queue_tail;
};

struct conn* createConnection(struct worker* worker, const char* ip_address, int port, int protocol, int naggles, int server);
int openTcpSocket(const char* ipAddress, int port);
int openUdpSocket(const char* ipAddress, int port);
int pushRequest(struct conn* conn, struct request* request);
struct request* getNextRequest(struct conn* conn);

#endif
