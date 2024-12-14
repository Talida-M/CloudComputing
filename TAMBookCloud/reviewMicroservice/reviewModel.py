from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.testing.suite.test_reflection import users
from rabbitmq import connect_rabbitmq, send_message
import uuid
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Review(db.Model):
    __tablename__= 'reviews'

    reviewDate = db.Column(db.Date, primary_key = True)
    idUser = db.Column(db.Integer, primary_key = True)
    idBook =  db.Column(db.Integer, primary_key = True)
    rating =  db.Column(db.Integer, nullable=False)
    comment =  db.Column(db.String(255), nullable=False)

    def __init__(self, reviewDate, idUser, idBook,rating,comment):
        self.reviewDate = reviewDate
        self.idUser = idUser
        self.idBook = idBook
        self.rating = rating
        self.comment = comment

    def to_dict(self):
        return {
            'reviewDate': self.reviewDate.isoformat(),
            'idUser': self.idUser,
            'idBook': self.idBook,
            'rating': self.rating,
            'comment': self.comment
        }

    @classmethod
    def create_review(cls, reviewDate, idUser, idBook, rating, comment):
        review = cls(reviewDate=reviewDate, idUser=idUser, idBook=idBook, rating=rating, comment=comment)
        db.session.add(review)
        db.session.commit()
        return review

    @classmethod
    def get_reviews_for_book(cls, idBook):
        return cls.query.filter_by(idBook=idBook).all()

    @classmethod
    def update_review(cls, reviewDate, idUser, idBook, rating=None, comment=None):
        review = cls.query.filter_by(reviewDate=reviewDate, idUser=idUser, idBook=idBook).first()
        if not review:
            return None
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        db.session.commit()
        return review

    @classmethod
    def delete_review(cls, reviewDate, idUser, idBook):
        review = cls.query.filter_by(reviewDate=reviewDate, idUser=idUser, idBook=idBook).first()
        if review:
            db.session.delete(review)
            db.session.commit()
        return review
