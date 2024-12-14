from flask_sqlalchemy import SQLAlchemy
from rabbitmq import connect_rabbitmq, send_message
from sqlalchemy import or_
import uuid

db = SQLAlchemy()

class Author(db.Model):
    __tablename__= 'authors'

    idAuthor = db.Column(db.Integer, primary_key = True)
    firstName = db.Column(db.String(255), nullable=False)
    lastName =  db.Column(db.String(255), nullable=False)

    def __init__(self, idAuthor, firstName, lastName):
        self.idAuthor = idAuthor
        self.firstName = firstName
        self.lastName = lastName


    @classmethod
    def get_all_authors(cls):
        authors = cls.query.all()
        return [author.to_dict() for author in authors]
    def to_dict(self):
        return {
            'idAuthor':self.idAuthor,
            'firstName':self.firstName,
            'lastName':self.lastName

        }

    @classmethod
    def add_author(cls, author_data):

        author = {
            'idAuthor': uuid.uuid4(),
            'firstName': author_data['firstName'],
            'lastName': author_data['lastName'],

        }
        send_message_to_queue(author)

        return 'Your author was successful registered'

    @classmethod
    def get_author_by_name(cls, author_data):
        lastName = author_data['lastName']
        firstName = author_data['firstName']

        authors = Author.query.filter(
            or_(
                Author.lastName == lastName,
                Author.lastName == firstName,
                Author.firstName == lastName,
                Author.firstName == firstName
            )
        ).all()

        if authors is not None:
            return authors
        else:
            return {"error": "Author not found", "status": 404}, 404

    @classmethod
    def delete_author_by_id(cls,author_data):
        idAuthor = author_data['idAuthor']

        author = Author.query.filter_by(idAuthor=idAuthor).first()

        if author is None:
            return {"error": "Author not found", "status": 404}, 404

        try:
            db.session.delete(author)
            db.session.commit()
            return {"message": f"Author '{idAuthor}' has been successfully deleted.", "status": 200}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete author: {str(e)}", "status": 500}, 500


def send_message_to_queue(author_data):
    channel = connect_rabbitmq()
    send_message(channel, 'author_queue',author_data)
    channel.close()