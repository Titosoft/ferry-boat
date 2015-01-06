ferry-boat
==========

A tool to manage docker containers. Powered by web2py.

Running on docker:

```
docker run -d --name ferryMQ dockerfile/rabbitmq
```
```
docker run --rm -e C_FORCE_ROOT=true -v /var/run/docker.sock:/var/run/docker.sock --link mq:mq dockerfile/rabbitmq --name ferry-boat -p 8000:80 titogarrido/ferry-boat
```
