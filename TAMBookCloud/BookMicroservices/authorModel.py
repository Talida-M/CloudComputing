from flask_sqlalchemy import SQLAlchemy
# from rabbitmq import connect_rabbitmq, send_message
from sqlalchemy import or_
import uuid

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
        return [author.to_dict() for author in authors]
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
    def get_author_by_name(cls, author_data):
        lastname = author_data['lastname']
        firstname = author_data['firstname']

        authors = Author.query.filter(
            or_(
                Author.lastname == lastname,
                Author.lastname == firstname,
                Author.firstname == lastname,
                Author.firstname == firstname
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

#
# def send_message_to_queue(author_data):
#     channel = connect_rabbitmq()
#     send_message(channel, 'author_queue',author_data)
#     channel.close()