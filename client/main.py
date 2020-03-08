from functools import reduce
import json
import math
import time

from decouple import config
import etcd3
import pika


ETCD_HOST = config('ETCD_HOST', default='localhost')
ETCD_PORT = config('ETCD_PORT', default='2379')
RABBIT_HOST = config('RABBITMQ_HOST', default='localhost')
RABBIT_PORT = config('RABBITMQ_PORT', default='5672')
RABBIT_QUEUE = config('RABBITMQ_QUEUE', default='calculation')
RABBIT_USER = config('RABBITMQ_USER')
RABBIT_PASS = config('RABBITMQ_PASS')


def process(calculation):
    function = calculation['function']
    args = calculation['arguments']

    if function == 'sum':
        result = math.fsum(args)
        status = 'done'
    elif function == 'subtract':
        if len(args) < 2:
            result = 'expected two or more arguments'
            status = 'error'
        else:
            result = args[0] - math.fsum(args[1:])
            status = 'done'
    elif function == 'multiply':
        if len(args) < 2:
            result = 'expected two or more arguments'
            status = 'error'
        else:
            result = reduce((lambda x, y: x*y), args)
            status = 'done'
    elif function == 'divide':
        if len(args) < 2:
            result = 'expected two or more arguments'
            status = 'error'
        else:
            try:
                result = reduce((lambda x, y: x/y), args)
                status = 'done'
            except ZeroDivisionError as e:
                result = str(e)
                status = 'error'
    else:
        result = 'invalid function'
        status = 'error'

    calculation['result'] = result
    calculation['status'] = status
    return calculation

def on_message(channel, method, properties, body):
    body = json.loads(body)
    uuid = body['uuid']
    print(f'Processing {uuid}')

    r = etcd.get(uuid)
    calculation = json.loads(r[0])
    print(calculation)
    calculation['status'] = 'processing'
    etcd.put(uuid, json.dumps(body))
    print(calculation)
    result = process(calculation)
    etcd.put(uuid, json.dumps(result))
    print(result)
    time.sleep(5)

    channel.basic_ack(delivery_tag=method.delivery_tag)


def start_listening():
    global etcd
    etcd = etcd3.client(host=ETCD_HOST,
                        port=ETCD_PORT)

    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    params = pika.ConnectionParameters(host=RABBIT_HOST,
                                       port=RABBIT_PORT,
                                       credentials=credentials)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE)

    channel.basic_consume(queue=RABBIT_QUEUE,
                          on_message_callback=on_message,
                          auto_ack=False)
    channel.start_consuming()

    return cpnnection, channel


if __name__ == '__main__':
    print('Starting client...')
    con, ch = start_listening()

#    if ch.is_open:
#        ch.close()
#    if con.is_open:
#        con.close()
