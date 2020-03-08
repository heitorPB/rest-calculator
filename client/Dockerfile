FROM python:3.8.2-slim

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY . /app/

CMD ["python", "/app/main.py"]
