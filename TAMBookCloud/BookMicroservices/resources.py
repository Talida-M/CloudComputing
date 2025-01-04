from flask_restful import Resource, reqparse
from models import Author,Book
# from authorModel import Author
# from bookModel import Book
from prometheus_client import Counter, Histogram
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


from flask import request, jsonify
parser = reqparse.RequestParser()
parser.add_argument('firstname', required=False, help="Author name")
parser.add_argument('lastname', required=False, help="Author name")

parser.add_argument('name', required=True, help="Book name cannot be blank")
parser.add_argument('price', required=True,type=int,  help="Price must be a number")
parser.add_argument('stockstatus', required=True,type=int,  help="Stock must be a number")
parser.add_argument('year', required=True, help="Year name cannot be blank")
parser.add_argument('name', required=True, help="Book name cannot be blank")
parser.add_argument('description', required=True, help="Book description cannot be blank")
parser.add_argument('publisher', required=True, help="Book publisher cannot be blank")
parser.add_argument('category', required=True, help="Book category cannot be blank")
parser.add_argument('idauthor', required=True, help="Book author id must be a string")

REQUEST_COUNT = Counter(
    'book_microservice_request_count',
    'Request Count for Book Microservice',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'book_microservice_request_latency_seconds',
    'Request Latency for Book Microservice',
    ['method', 'endpoint','trace_id'],
    buckets=[0.00001,0.05,0.1,0.25,0.5, 1.0, 2.0, 5.0, 10.0]
)

class DelAuthorApi(Resource):#by id
    def delete(self, idauthor):
        message = Author.delete_author_by_id(idauthor)
        return message,200

class AuthorsAPI(Resource):#by names
    def get(self):
        start_time = time.time()
        endpoint = '/api/author/'
        authors = Author.get_all_authors()

        REQUEST_COUNT.labels('GET', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if authors:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully fetched {len(authors)} authors"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No authors available"
            })
        REQUEST_LATENCY.labels('GET', endpoint, trace_id).observe(time.time() - start_time)
        return [author.to_dict() for author in authors], 200

    def post(self):
        start_time = time.time()
        endpoint = '/api/author/'
        args = parser.parse_args()
        author = {
            'firstname': args['firstname'],
            'lastname': args['lastname'],
        }
        author_done = Author.add_author(author)

        REQUEST_COUNT.labels('POST', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully created {author_done['idauthor']} author"
        })
        REQUEST_LATENCY.labels('POST', endpoint, trace_id).observe(time.time() - start_time)
        return {'authorid':author_done['idauthor']}, 201

class AuthorAPI(Resource):#by names
    def get(self,lastname,firstname):
        start_time = time.time()
        endpoint = '/api/author/'
        authors = Author.get_author_by_name( lastname,firstname)

        REQUEST_COUNT.labels('GET', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if authors:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully fetched {len(authors)} authors"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No authors available"
            })
        REQUEST_LATENCY.labels('GET', endpoint, trace_id).observe(time.time() - start_time)

        return [author.to_dict() for author in authors], 200

class BookAPI(Resource):#by names
    def get(self,name):
        books = Book.get_book_by_name(name)
        return [book.to_dict() for book in books], 200
        # book = Book.get_book_by_name(name)
        # if book:
        #     return book, 200
        # return {'message': 'Book not found'}, 404

class BookByiD(Resource):
    def get(self,idbook):
        start_time = time.time()
        endpoint = f'/api/book/byid/{idbook}'
        book = Book.get_book_by_id(idbook)
        REQUEST_COUNT.labels('GET', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if book:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully find book with id {idbook}"
            })
            REQUEST_LATENCY.labels('GET', endpoint, trace_id).observe(time.time() - start_time)
            return book, 200
        logger.info({
            "date": datetime.today().date().isoformat(),
            "user-id": user_id,
            "trace_id": trace_id,
            "message": "The book doesn't exist"
        })
        return {'message': 'Book not found'}, 404

class BookByiDs(Resource):
    def post(self):
        try:
            data = request.get_json()
            idbooks = data.get('idbooks', [])
            if not idbooks:
                return jsonify({'error': 'No book IDs provided'}), 400
            books = Book.get_books_by_ids(idbooks)
            if not books:
                return jsonify({'error': 'No books found for the given IDs'}), 404
            return jsonify([book.to_dict() for book in books])
        except Exception as e:
            return jsonify({'error': f'Failed to fetch books: {str(e)}'}), 500


class BooksAPI(Resource):
    def get(self):
        start_time = time.time()
        endpoint = '/api/book/'
        books = Book.get_all_books()
        REQUEST_COUNT.labels('GET', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if books:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id":user_id,
                "trace_id": trace_id,
                "message": f"Successfully fetched {len(books)} books"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No books available"
            })
        REQUEST_LATENCY.labels('GET', endpoint,trace_id).observe(time.time() - start_time)
        return [book.to_dict() for book in books], 200

    def update(self, idbook, stockstatus):
        start_time = time.time()
        endpoint = '/api/book/'
        review = Book.update_book_stock(idbook, stockstatus)

        REQUEST_COUNT.labels('PUT', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if review:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully update {idbook} book"
            })

        REQUEST_LATENCY.labels('PUT', endpoint, trace_id).observe(time.time() - start_time)


        return review, 200

    def post(self):

        start_time = time.time()
        endpoint = '/api/book/'

        args = parser.parse_args()
        book = {
            'name': args['name'],
            'price': args['price'],
            'stockstatus': args['stockstatus'],
            'year': args['year'],
            'description': args['description'],
            'publisher': args['publisher'],
            'category': args['category'],
            'idauthor': args['idauthor']
        }
        book_done = Book.add_book(book)

        REQUEST_COUNT.labels('POST', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if book_done:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Successfully created '{book_done['idbook']}' book"
            })

        REQUEST_LATENCY.labels('POST', endpoint, trace_id).observe(time.time() - start_time)

        return {'idbook':book_done['idbook']}, 201

class DelBookApi(Resource):  # by id
    def delete(self, idbook):
        message = Book.delete_book_by_id(idbook)
        return message, 200
