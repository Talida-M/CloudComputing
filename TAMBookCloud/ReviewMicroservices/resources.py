from datetime import datetime

from flask_restful import Resource, reqparse
import os

from sqlalchemy.dialects.mysql import DATETIME

from reviewModel import Review

parser = reqparse.RequestParser()
# parser.add_argument('reviewDate', required=True, help="ISBN of the book cannot be blank")
parser.add_argument('idUser', required=True,type=int, help="User id cannot be blank")
parser.add_argument('idBook', required=True, type=int,help="Book id cannot be blank")
parser.add_argument('rating', required=True,type=int,  help="Rating must be a number")
parser.add_argument('comment', required=True, help="Comment cannot be blank")

class ReviewAPI(Resource):
    def get(self, idBook):
        reviews = Review.get_reviews_for_book(idBook)
        return reviews, 200

    def delete(self, idBook, reviewDate, idUser):
        review_date = datetime.strptime(reviewDate, '%Y-%m-%d').date()
        message = Review.delete_review(review_date,idUser,idBook)
        return message,200

class ReviewsAPI(Resource):
    def update(self):
        args = parser.parse_args()
        new_review = {
            'reviewDate': args['reviewDate'],
            'idUser': args['idUser'],
            'idBook': args['idBook'],
            'rating': args['rating'],
            'comment': args['comment']
        }
        review = Review.update_review(new_review['reviewDate'],new_review['idUser'],new_review['idBook'],new_review['rating'],new_review['comment'])
        return review,200

    def post(self):
        args = parser.parse_args()
        review = {
            'reviewDate': datetime.today().date(),
            'idUser': args['idUser'],
            'idBook': args['idBook'],
            'rating': args['rating'],
            'comment': args['comment']
        }
        review_done = Review.create_review(review)
        return {'bookId':review_done['idBook']}, 201