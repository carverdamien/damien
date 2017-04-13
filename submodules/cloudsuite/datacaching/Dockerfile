FROM gcc
WORKDIR /home
COPY twitter_dataset ./twitter_dataset
COPY memcached_client ./memcached_client
RUN make -C memcached_client
