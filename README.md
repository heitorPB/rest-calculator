# Simple REST Calculator

Simple REST API to do simple math.


## Architecture

The server receives HTTP requests with instructions to calculate. This is
stored in the database and queued to be processed latter. The clients get an
instruction from the queue, process it and store in the databse.

The server can check the stauts of a calculation. It can be one of: `queued`,
`processing`, `done` or `error`.

Techs used:
- [etcd](https://etcd.io) as key-value store
- [RabbitMQ](https://www.rabbitmq.com) as messaging system
- [FastAPI](https://fastapi.tiangolo.com) as the web framework

### Endpoints

This system has 3 endpoints:

- POST `/`: to queue a calculation
- GET `/status/{request_id}`: to query the status of a calculation
- GET `/results/{request_id}`: to query the result of a calculation


## Running

### Docker

The simplest way:

```
$ docker-compose up -d --scale client=3
```

This will fire etcd, rabbitmq, the server and 3 clients.

RabbitMQ provides a [web Management system](http://localhost:15672).

etcd provides [metrics](http://localhost:2379/metrics) and [health
check](http://localhost:2379/health) for monitoring.

### In a terminal

It's also possible to run the server and the client in the terminal. They
require a RabbitMQ and etcd instances somewhere. The default is to check
`localhost` on their default ports, but it can be changed with environment
variables. Check the [docker-compose](docker-compose.yml) file for details.

The RabbitMQ needs authentication, to pass the user and password to the
clients, use env vars:

```
$ RABBITMQ_USER=galileo RABBITMQ_PASS=abc123 python server/main.py
$ RABBITMQ_USER=galileo RABBITMQ_PASS=abc123 python client/main.py
```

## Using

After the system boots up (might take a while, but less than a minute), check
the online documentation at:

- [swagger](http://localhost/docs)
- [redoc](http://localhost/redoc)

A simple way to test the system is to access the swagger and use the `Try it
out` buttons on each endpoint.

## License

Distributed under the GNU GPLv3. See [LICENSE](LICENSE) for details.
