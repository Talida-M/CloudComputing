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


# RabbitMQ connection settings
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')

# Function to connect to RabbitMQ
# def connect_rabbitmq():
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
#     channel = connection.channel()
#     return channel
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

# Function to declare the queue
# def declare_queue(channel, queue_name='order_queue'):
#     channel.queue_declare(queue=queue_name, durable=True)

# Function to send a message to a queue
# def send_message(message,queue_name="order_queue"):#,channel=connect_rabbitmq()):
#     channel = connect_rabbitmq()
#     message_json = json.dumps(message)
#     print(message_json)
#     channel.basic_publish(
#         exchange='',
#         routing_key=queue_name,
#         body=message_json,
#         properties=pika.BasicProperties(
#             delivery_mode=2,  # Make the message persistent
#         )
#     )
#     print(f"Sent message to queue: {message}")
def send_message_order(channel, queue_name, message):
    message_json = json.dumps(message)
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
        "message": f"Sent message to queue: {message}"
    })
    print(f"Sent message to queue: {message}")
# Function to consume messages from a queue
# def consume_messages(channel, queue_name='order_queue', callback=None):
#     declare_queue(channel, queue_name)
#     channel.basic_qos(prefetch_count=1)
#     channel.basic_consume(queue=queue_name, on_message_callback=callback)
#     print("Waiting for messages...")
#     channel.start_consuming()
