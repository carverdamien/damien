FROM gcc
COPY anon.c .
RUN gcc -o anon anon.c
ENTRYPOINT [ "./anon" ]
CMD [ "1073741824", "30" ]
