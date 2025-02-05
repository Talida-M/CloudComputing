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
        self.stockstatus = stockstatus
        self.year = year
        self.description = description
        self.publisher = publisher
        self.category = category
        self.idauthor = idauthor


    @classmethod
    def get_all_books(cls):
        books = cls.query.all()
        return [book for book in books]
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

    @classmethod
    def add_book(cls, book_data):
        book = Book(idbook=uuid.uuid4(),
            name= book_data['name'],
            price= book_data['price'],
            stockstatus=book_data['stockstatus'],
            year=book_data['year'],
            description=book_data['description'],
            publisher=book_data['publisher'],
            category=book_data['category'],
            idauthor=book_data['idauthor'])

        db.session.add(book)
        db.session.commit()

    @classmethod
    def get_book_by_id(cls, idbook):
        book = Book.query.filter_by(idbook=idbook).first()
        return book.to_dict() if book else None

    @classmethod
    def get_books_by_ids(cls,idbooks):
        books = Book.query.filter(Book.idbook.in_(idbooks)).all()
        if books is not None:
            return books

    @classmethod
    def get_book_by_name(cls, name):
        books = Book.query.filter_by(name=name).all()
        if books is not None:
            return books

    @classmethod
    def update_book_stock(cls, idbook, stockstatus):
        book = Book.query.filter_by(idbook=idbook).first()
        if not book:
            return None
        if stockstatus is not None:
            book.stockstatus = stockstatus

        db.session.commit()
        return book


    @classmethod
    def delete_book_by_id(cls, idbook):
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
