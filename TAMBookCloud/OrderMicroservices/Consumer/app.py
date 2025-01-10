import pika
import psycopg
import json
import os
from rabbitmq import consume_messages

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
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'db')
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my-secret-pw')

# PostgreSQL connection setup
def get_postgres_connection():
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    return conn

def update_order_status(order_data):
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE idorder = %s
                """,
                ("success", order_data['idorder'])
            )
            conn.commit()
            cursor.execute(
                """
                SELECT status FROM orders WHERE idorder = %s
                """,
                (order_data['idorder'],)
            )
            updated_status = cursor.fetchone()[0]
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-type": 'admin',
                "trace_id": 'N/A',
                "message": f"for order {order_data['idorder']} status updated to {updated_status}"
            })
    finally:
        conn.close()
#"UPDATE orders SET status = 'success' WHERE orders.idorder = order_data['idorder']"
def callback(ch, method, properties, body):
    print(f"Received the new order message")
    order_data = json.loads(body)
    print(f"the order is received with status {order_data['status']} for order {order_data['idorder']}")
    logger.info({
        "date": datetime.today().date().isoformat(),
        "user-type": 'admin',
        "trace_id": 'N/A',
        "message": f"the order is received with status {order_data['status']} for {order_data['idorder']}"
    })
    update_order_status(order_data)
    # Acknowledge the message to RabbitMQ (message has been processed)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up RabbitMQ connection and channel
def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    consume_messages(channel, queue_name='order_queue', callback=callback)

if __name__ == '__main__':
    start_consuming()
