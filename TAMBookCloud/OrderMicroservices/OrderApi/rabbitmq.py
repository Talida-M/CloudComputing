import pika
import json
import os
import time
from datetime import datetime

import logging
from logging.handlers import SysLogHandler
syslog_host = 'syslog-ng'
syslog_port = 514
logger = logging.getLogger('book_microservice')
logger.setLevel(logging.INFO)


syslog_handler = SysLogHandler(address=(syslog_host, syslog_port))
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

def connect_rabbitmq(retries=5, delay=5):
    for attempt in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            print("Connect to chanel success")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise RuntimeError("Failed to connect to RabbitMQ after several attempts.")

def send_message_order(channel, queue_name, message):
    message_json = json.dumps(message)
    idorder = message['idorder']
    iduser = message['iduser']
    status = message['status']
    totalprice = message['totalprice']
    print(message_json)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message_json,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make the message persistent
        )
    )
    logger.info({
        "date": datetime.today().date().isoformat(),
        "user-type": 'admin',
        "trace_id": 'N/A',
        "message": f"Sent message to queue idorder: {idorder}, iduser: {iduser}, status: {status}, totalprice: {totalprice}"
    })
    print(f"Sent message to queue: idorder: {idorder}, iduser: {iduser}, status: {status}, totalprice: {totalprice}")
