from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Review(db.Model):
    __tablename__= 'reviews'

    reviewdate = db.Column(db.Date, nullable=False)
    iduser = db.Column(db.String, nullable=False)
    idbook =  db.Column(db.String, nullable=False)
    rating =  db.Column(db.Integer, nullable=False)
    comment =  db.Column(db.String(255), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('reviewdate', 'iduser', 'idbook'),
    )
    def __init__(self, reviewdate, iduser, idbook,rating,comment):
        self.reviewdate = reviewdate
        self.iduser = iduser
        self.idbook = idbook
        self.rating = rating
        self.comment = comment

    def to_dict(self):
        return {
            'reviewdate': self.reviewdate.strftime('%Y-%m-%d'),#.isoformat(),
            'iduser': self.iduser,
            'idbook': self.idbook,
            'rating': self.rating,
            'comment': self.comment
        }

    # @classmethod
    # def create_review(cls, reviewDate, idUser, idBook, rating, comment):
    #     review = cls(reviewDate=reviewDate, idUser=idUser, idBook=idBook, rating=rating, comment=comment)
    #     db.session.add(review)
    #     db.session.commit()
    #     return review
    @classmethod
    def create_review(cls, review_data):
        review=Review(reviewdate= datetime.today().date(),
        iduser= review_data['iduser'],
        idbook= review_data['idbook'],
        rating= review_data['rating'],
        comment= review_data['comment']
        )
        db.session.add(review)
        db.session.commit()
        return review

    @classmethod
    def get_reviews_for_book(cls, idbook):
        return cls.query.filter_by(idbook=idbook).all()

    @classmethod
    def update_review(cls, reviewdate, iduser, idbook, rating=None, comment=None):
        review = cls.query.filter_by(reviewdate=reviewdate, iduser=iduser, idbook=idbook).first()
        if not review:
            return None
        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment
        db.session.commit()
        return review

    @classmethod
    def delete_review(cls, reviewdate, iduser, idbook):
        review = cls.query.filter_by(reviewdate=reviewdate, iduser=iduser, idbook=idbook).first()
        if review:
            db.session.delete(review)
            db.session.commit()
            return {"message": f"Review has been successfully deleted."}, 200
        return {"message": f"Failed to delete the review.Not found"}, 404

# def send_message_to_queue(bookid_data):
#     channel = connect_rabbitmq()
#     send_message(channel, 'book_queue', bookid_data)
#     channel.close()