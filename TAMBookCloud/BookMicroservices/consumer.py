import pika
import psycopg
import json
import os

# Environment variables for RabbitMQ and PostgreSQL connection
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


# Function to check if a book exists by ISBN
def book_exists(idbook):
    print(f"laaaaaaaaaa{idbook}")
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS (SELECT 1 FROM books WHERE idbook = %s",(idbook,))
    exists_b = cursor.fetchone()[0]
    conn.close()
    return exists_b

# Callback function that will be triggered when a message is received from RabbitMQ
def callback(ch, method, properties, body):
    print("Received a new idbook message")

    bookid_data = json.loads(body)
    book_id = bookid_data['idbook']

    exists_book = book_exists(book_id)

    response = {'exists': exists_book}

    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
        ),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set up RabbitMQ connection and channel
def start_service():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='check_book_existence')

    # Consume the request for checking book existence
    channel.basic_consume(queue='check_book_existence', on_message_callback=callback)

    print("BookService: Awaiting book existence check requests...")
    channel.start_consuming()

if __name__ == '__main__':
    start_service()
