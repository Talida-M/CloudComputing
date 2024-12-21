import pika
import psycopg
import json
import os
from rabbitmq import consume_messages

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
def book_exists(isbn):
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM books WHERE isbn = %s", (isbn,))
            return cursor.fetchone() is not None
    finally:
        conn.close()

# Function to add a book to the database
def add_book_to_db(book_data):
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO books (isbn, name, author, pages) VALUES (%s, %s, %s, %s)",
                (book_data['isbn'], book_data['name'], book_data['author'], book_data['pages'])
            )
            conn.commit()
    finally:
        conn.close()

# Callback function that will be triggered when a message is received from RabbitMQ
def callback(ch, method, properties, body):
    print("Received the new order message")

    order_data = json.loads(body)
    print(order_data)
    # if not book_exists(book_data['isbn']):
    #     print(f"Book with ISBN {book_data['isbn']} does not exist, adding to the database.")
    #     # add_book_to_db(book_data)
    # else:
    #     print(f"Book with ISBN {book_data['isbn']} already exists, skipping insertion.")

    # Acknowledge the message to RabbitMQ (message has been processed)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up RabbitMQ connection and channel
def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    consume_messages(channel, queue_name='order_queue', callback=callback)

if __name__ == '__main__':
    start_consuming()
