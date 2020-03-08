from enum import Enum
import json
from typing import List
from uuid import UUID, uuid4

from decouple import config
import etcd3
from fastapi import FastAPI
import pika
from pydantic import BaseModel


ETCD_HOST = config('ETCD_HOST', default='localhost')
ETCD_PORT = config('ETCD_PORT', default='2379')
RABBIT_HOST = config('RABBITMQ_HOST', default='localhost')
RABBIT_PORT = config('RABBITMQ_PORT', default='5672')
RABBIT_QUEUE = config('RABBITMQ_QUEUE', default='calculation')
RABBIT_USER = config('RABBITMQ_USER')
RABBIT_PASS = config('RABBITMQ_PASS')


app = FastAPI(title='Simple REST Calculator',
              description='Basic math through json',
              version='0.3.1')

etcd = None
# RabbitMQ stuff
connection = None
channel = None

@app.on_event('startup')
def startup_event():
    # TODO add some checks here for success
    global etcd
    etcd = etcd3.client(host=ETCD_HOST,
                        port=ETCD_PORT)

    global connection
    global channel
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST,
                                       port=RABBIT_PORT,
                                       credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE)


@app.on_event('shutdown')
def shutdown_event():
    if channel.is_open:
        channel.close()
    if connection.is_open:
        connection.close()


class Function(str, Enum):
    sum = "sum"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

class Calculation(BaseModel):
    function: Function
    arguments: List[float]


@app.post('/')
async def root(calculation: Calculation):
    uuid = uuid4()
    data = {'function': calculation.function,
            'arguments': calculation.arguments,
            'status': 'queued',
            'result': ''}

    body = json.dumps(data)
    r = etcd.put(str(uuid), body)

    payload = {'uuid': str(uuid)}
    payload = json.dumps(payload)
    if not channel.is_open:
        startup_event()
    channel.basic_publish(exchange='', # use default one
                          routing_key=RABBIT_QUEUE,
                          body=payload,
                          properties=pika.BasicProperties(delivery_mode=2),
                         )

    return {'id': uuid}


@app.get('/status/{request_id}')
async def status(request_id: str):
    calculation = etcd.get(request_id)
    data = calculation[0]

    if data is not None:
        data = json.loads(data)

        return {'status': data['status']}
    else:
        return {'status': 'invalid key'}


@app.get('/results/{request_id}')
async def result(request_id: str):
    calculation = etcd.get(request_id)
    data = calculation[0]

    if data is not None:
        data = json.loads(data)

        return {'result': data['result']}
    else:
        return {'result': 'invalid key'}