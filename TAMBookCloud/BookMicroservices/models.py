import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
db = SQLAlchemy()

class Author(db.Model):
    __tablename__= 'authors'

    idauthor = db.Column(db.String, primary_key = True)
    firstname = db.Column(db.String(255), nullable=False)
    lastname =  db.Column(db.String(255), nullable=False)

    def __init__(self, idauthor, firstname, lastname):
        self.idauthor = idauthor
        self.firstname = firstname
        self.lastname = lastname


    @classmethod
    def get_all_authors(cls):
        authors = cls.query.all()
        return [author for author in authors]
    def to_dict(self):
        return {
            'idauthor':self.idauthor,
            'firstname':self.firstname,
            'lastname':self.lastname

        }

    @classmethod
    def add_author(cls, author_data):
        author = Author(idauthor= uuid.uuid4(),
        firstname= author_data['firstname'],
        lastname= author_data['lastname'])

        db.session.add(author)
        db.session.commit()
        return author

    @classmethod
    def get_author_by_name(cls, lastname, firstname):

        authors = Author.query.filter(
            or_(
                Author.lastname == lastname and Author.firstname == firstname,
                Author.lastname == firstname and Author.firstname == lastname,
            )
        ).all()

        if authors is not None:
            return authors
        else:
            return {"error": "Author not found", "status": 404}, 404

    @classmethod
    def delete_author_by_id(cls,idauthor):

        author = Author.query.filter_by(idauthor=idauthor).first()

        if author is None:
            return {"error": "Author not found", "status": 404}, 404

        try:
            db.session.delete(author)
            db.session.commit()
            return {"message": f"Author '{idauthor}' has been successfully deleted.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete author: {str(e)}", "status": 500}, 500


class Book(db.Model):
    __tablename__= 'books'

    idbook = db.Column(db.String, primary_key = True)
    name = db.Column(db.String(255), nullable=False)
    price =  db.Column(db.Float, nullable=False)
    stockstatus =  db.Column(db.Integer, nullable=False)
    year =  db.Column(db.String(4), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    idauthor = db.Column(db.String, db.ForeignKey('authors.idauthor'), nullable=False)  # Foreign Key

    author = db.relationship('Author', backref='books', lazy=True)

    def __init__(self, idbook, name, price,stockstatus,year,description,publisher,category,idauthor):
        self.idbook = idbook
        self.name = name
        self.price = price
        self.stockStatus = stockstatus
        self.year = year
        self.description = description
        self.publisher = publisher
        self.category = category
        self.idauthor = idauthor


    @classmethod
    def get_all_books(cls):
        books = cls.query.all()
        return [book.to_dict() for book in books]
    def to_dict(self):
        return {
            'idbook': self.idbook,
            'name':self.name,
            'price':self.price,
            'stockstatus':self.stockstatus,
            'year':self.year,
            'description':self.description,
            'publisher':self.publisher,
            'category':self.category,
            'authorname': f"{self.author.firstname} {self.author.lastname}" if self.author else None

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
    #     idauthor=new_author.idauthor  # Bind to the author's id
    # )
    # db.session.add(new_book)
    # db.session.commit()
    @classmethod
    def add_book(cls, book_data):

        book = {
            'idbook': uuid.uuid4(),
            'name': book_data['name'],
            'price': book_data['price'],
            'stockstatus':book_data['stockstatus'],
            'year':book_data['year'],
            'description':book_data['description'],
            'publisher':book_data['publisher'],
            'category':book_data['category'],
            'idauthor':book_data['idauthor']


        }
      #  send_message_to_queue(book)

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
        idbook = book_data['idbook']
        stock = book_data['stockstatus']

        book = Book.query.filter_by(idbook=idbook).first()

        if book is None:
            return {"error": "Book not found", "status": 404}, 404

        try:
            book.stockStatus = stock
            db.session.commit()
            return {"message": f"Book '{idbook}' stock has been updated to '{stock}'.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update book status: {str(e)}", "status": 500}, 500

    @classmethod
    def delete_book_by_id(cls, idbook):

        # Query the database
        book = Book.query.filter_by(idbook=idbook).first()

        if book is None:
            return {"error": "Book not found", "status": 404}, 404

        try:
            db.session.delete(book)
            db.session.commit()
            return {"message": f"Book '{idbook}' has been successfully deleted.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete book: {str(e)}", "status": 500}, 500
