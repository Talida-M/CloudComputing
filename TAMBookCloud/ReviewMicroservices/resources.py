from datetime import datetime
from flask import request
from flask_restful import Resource, reqparse
import os

from sqlalchemy.dialects.mysql import DATETIME


from reviewModel import Review

parser = reqparse.RequestParser()
parser.add_argument('reviewdate', required=True, help="date cannot be blank")
parser.add_argument('iduser', required=True, help="User id cannot be blank")
parser.add_argument('idbook', required=True,help="Book id cannot be blank")
parser.add_argument('rating', required=True,type=int,  help="Rating must be a number")
parser.add_argument('comment', required=True, help="Comment cannot be blank")

class ReviewAPI(Resource):
    def get(self, idbook):
        reviews = Review.get_reviews_for_book(idbook)
        # return reviews, 200
        return [review.to_dict() for review in reviews], 200

class DelReviewApi(Resource):
    def delete(self, idbook, reviewdate, iduser):
        review_dates = datetime.strptime(reviewdate, '%Y-%m-%d').date()
        message = Review.delete_review(review_dates,iduser,idbook)
        return message,200

class ReviewsAPI(Resource):
    def update(self):
        args = parser.parse_args()
        new_review = {
            'reviewdate': args['reviewdate'],
            'iduser': args['iduser'],
            'idbook': args['idbook'],
            'rating': args['rating'],
            'comment': args['comment']
        }
        review = Review.update_review(new_review['reviewdate'],new_review['iduser'],new_review['idbook'],new_review['rating'],new_review['comment'])
        return review,200

    def post(self):
        data = request.get_json()
        review = {
            'reviewdate': datetime.today().date(),
            'iduser': data['iduser'],
            'idbook': data['idbook'],
            'rating': data['rating'],
            'comment': data['comment']
        }
        review_done = Review.create_review(review)
        return review_done, 200
        # return {'bookid':review_done['idbook']}, 200
    # def post(self):
    #     args = parser.parse_args()
    #     review = {
    #         'reviewdate': datetime.today().date(),
    #         'iduser': args['iduser'],
    #         'idbook': args['idbook'],
    #         'rating': args['rating'],
    #         'comment': args['comment']
    #     }
    #     review_done = Review.create_review(review)
    #     return review_done, 200
    #     # return {'bookid':review_done['idbook']}, 200