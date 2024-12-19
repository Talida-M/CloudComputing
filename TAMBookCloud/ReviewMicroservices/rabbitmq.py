# import pika
# import json
# import os
# import uuid
# # RabbitMQ connection settings
# RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
#
#
# def connect_rabbitmq():
#     connection = pika.BlockingConnection(
#         pika.ConnectionParameters(host=RABBITMQ_HOST))
#     channel = connection.channel()
#     return connection, channel
#
#
# def send_message_with_response(queue_name, message):
#     print(f"Sending message {json.dumps(message)} to {queue_name}")
#     try:
#         connection, channel = connect_rabbitmq()
#
#         response_queue = channel.queue_declare(
#             queue='', exclusive=True).method.queue
#         correlation_id = str(uuid.uuid4())
#         response = None
#
#         def on_response(ch, method, props, body):
#             nonlocal response
#             if correlation_id == props.correlation_id:
#                 response = json.loads(body)
#
#         channel.basic_consume(
#             queue=response_queue,
#             on_message_callback=on_response,
#             auto_ack=True
#         )
#
#         channel.basic_publish(
#             exchange='',
#             routing_key=queue_name,
#             properties=pika.BasicProperties(
#                 reply_to=response_queue,
#                 correlation_id=correlation_id
#             ),
#             body=json.dumps(message)
#         )
#
#         while response is None:
#             connection.process_data_events()
#
#         connection.close()
#         return response
#     except pika.exceptions.AMQPConnectionError as e:
#         raise ConnectionError("Failed to connect to RabbitMQ") from e
#     except TimeoutError as e:
#         raise TimeoutError("RabbitMQ response timeout") from e
#     finally:
#         if connection and connection.is_open:
#             connection.close()
