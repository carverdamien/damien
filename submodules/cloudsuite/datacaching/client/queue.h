#ifndef QUEUE_H
#define QUEUE_H

#define QUEUE_LEN(len, queue, head, tail, size) ({	\
      len = tail - head;				\
      if (head > size && tail > size) {			\
	head %= size;					\
	tail %= size;					\
      }							\
    })

#define QUEUE_PUSH(obj, queue, head, tail, size) ({	\
      queue[tail % size] = obj;				\
      tail++;						\
    })

#define QUEUE_POP(obj, queue, head, tail, size) ({	\
      obj = queue[head%size];				\
      head++;						\
    })
#endif
