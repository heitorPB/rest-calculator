from enum import Enum
import json
from typing import List
from uuid import UUID, uuid4

import etcd3
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
etcd = etcd3.client(host='localhost',
                    port=2379)


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

    r = etcd.put(str(uuid), json.dumps(data))

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