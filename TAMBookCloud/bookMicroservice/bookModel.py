from flask_sqlalchemy import SQLAlchemy
from rabbitmq import connect_rabbitmq, send_message
import uuid

db = SQLAlchemy()

class Book(db.Model):
    __tablename__= 'books'

    idBook = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable=False)
    price =  db.Column(db.Float, nullable=False)
    stockStatus =  db.Column(db.Integer, nullable=False)
    year =  db.Column(db.String(4), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    idAuthor = db.Column(db.Integer, db.ForeignKey('authors.idAuthor'), nullable=False)  # Foreign Key

    author = db.relationship('Author', backref='books', lazy=True)

    def __init__(self, idBook, name, price,stockStatus,year,description,publisher,category,idAuthor):
        self.idBook = idBook
        self.name = name
        self.price = price
        self.stockStatus = stockStatus
        self.year = year
        self.description = description
        self.publisher = publisher
        self.category = category
        self.idAuthor = idAuthor


    @classmethod
    def get_all_books(cls):
        books = cls.query.all()
        return [book.to_dict() for book in books]
    def to_dict(self):
        return {
            'idBook': self.idBook,
            'name':self.name,
            'price':self.price,
            'stockStatus':self.stockStatus,
            'year':self.year,
            'description':self.description,
            'publisher':self.publisher,
            'category':self.category,
            'authorName': f"{self.author.firstName} {self.author.lastName}" if self.author else None

        }

#exemplu de adaugare carte cu author FK
    # new_author = Author(name="J.K. Rowling", biography="Author of the Harry Potter series.")
    # db.session.add(new_author)
    # db.session.commit()
    # new_book = Book(
    #     idBook=1,
    #     name="Harry Potter and the Sorcerer's Stone",
    #     price=19.99,
    #     stockStatus=10,
    #     year="1997",
    #     description="Fantasy novel.",
    #     publisher="Bloomsbury",
    #     category="Fantasy",
    #     idAuthor=new_author.idAuthor  # Bind to the author's id
    # )
    # db.session.add(new_book)
    # db.session.commit()
    @classmethod
    def add_book(cls, book_data):

        book = {
            'idBook': uuid.uuid4(),
            'name': book_data['name'],
            'price': book_data['price'],
            'stockStatus':book_data['stockStatus'],
            'year':book_data['year'],
            'description':book_data['description'],
            'publisher':book_data['publisher'],
            'category':book_data['category'],
            'idAuthor':book_data['idAuthor']


        }
        send_message_to_queue(book)

        return 'Your book was successful registered'

    @classmethod
    def get_book_by_name(cls, book_data):
        name = book_data['name']

        books = Book.query.filter_by(name=name).all()
        if books is not None:
            return books
        else:
            return {"error": "Book not found", "status": 404}, 404


    @classmethod
    def update_book_stock(cls, book_data):
        idBook = book_data['idBook']
        stock = book_data['stockStatus']

        book = Book.query.filter_by(idBook=idBook).first()

        if book is None:
            return {"error": "Book not found", "status": 404}, 404

        try:
            book.stockStatus = stock
            db.session.commit()
            return {"message": f"Book '{idBook}' stock has been updated to '{stock}'.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update book status: {str(e)}", "status": 500}, 500

    @classmethod
    def delete_book_by_id(cls, book_data):
        idBook = book_data['idBook']

        # Query the database
        book = Book.query.filter_by(idBook=idBook).first()

        if book is None:
            return {"error": "Book not found", "status": 404}, 404

        try:
            db.session.delete(book)
            db.session.commit()
            return {"message": f"Book '{idBook}' has been successfully deleted.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete book: {str(e)}", "status": 500}, 500


def send_message_to_queue(book_data):
    channel = connect_rabbitmq()
    send_message(channel, 'book_queue',book_data)
    channel.close()