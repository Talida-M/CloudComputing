from datetime import datetime

from flask_restful import Resource, reqparse
import os

from models import Author,Book
# from authorModel import Author
# from bookModel import Book

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


class DelAuthorApi(Resource):#by id
    def delete(self, idauthor):
        message = Author.delete_author_by_id(idauthor)
        return message,200

class AuthorsAPI(Resource):#by names
    def get(self):
        authors = Author.get_all_authors()
        return [author.to_dict() for author in authors], 200

    def post(self):
        args = parser.parse_args()
        author = {
            'firstname': args['firstname'],
            'lastname': args['lastname'],
        }
        author_done = Author.add_author(author)
        return {'authorid':author_done['idauthor']}, 201

class AuthorAPI(Resource):#by names
    def get(self,lastname,firstname):
        authors = Author.get_author_by_name( lastname,firstname)
        return [author.to_dict() for author in authors], 200

class BookAPI(Resource):#by names
    def get(self,name):
        books = Book.get_book_by_name(name)
        return [book.to_dict() for book in books], 200


class BooksAPI(Resource):
    def get(self):
        books = Book.get_all_books()
        return [book.to_dict() for book in books], 200

    def update(self, idbook, stockstatus):
        review = Book.update_book_stock(idbook, stockstatus)
        return review, 200

    def post(self):
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
        return {'idbook':book_done['idbook']}, 201

class DelBookApi(Resource):  # by id
    def delete(self, idbook):
        message = Book.delete_book_by_id(idbook)
        return message, 200
