from datetime import datetime

import pytz
from flask import request
from flask_restful import Resource, reqparse
import os

from sqlalchemy.dialects.mysql import DATETIME


from reviewModel import Review

from prometheus_client import Counter, Histogram
import time

import logging
from logging.handlers import SysLogHandler
syslog_host = 'syslog-ng'
syslog_port = 514
logger = logging.getLogger('review_microservice')
logger.setLevel(logging.INFO)

syslog_handler = SysLogHandler(address=(syslog_host, syslog_port))
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

parser = reqparse.RequestParser()
parser.add_argument('reviewdate', required=True, help="date cannot be blank")
parser.add_argument('iduser', required=True, help="User id cannot be blank")
parser.add_argument('idbook', required=True,help="Book id cannot be blank")
parser.add_argument('rating', required=True,type=int,  help="Rating must be a number")
parser.add_argument('comment', required=True, help="Comment cannot be blank")

REQUEST_COUNT = Counter(
    'review_microservice_request_count',
    'Request Count for Book Microservice',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'review_microservice_request_latency_seconds',
    'Request Latency for Book Microservice',
    ['method', 'endpoint','trace_id'],
    buckets=[0.00001,0.05,0.1,0.25,0.5, 1.0, 2.0, 5.0, 10.0]
)

class ReviewAPI(Resource):
    def get(self, idbook):
        start_time = time.time()
        endpoint = f'/api/review/{idbook}'
        reviews = Review.get_reviews_for_book(idbook)
        REQUEST_COUNT.labels('GET', endpoint, 200).inc()

        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        buc_tz = pytz.timezone('Europe/Bucharest')
        current_time = datetime.now(buc_tz)

        if reviews:
            logger.info({
                "date": current_time.strftime("%d-%m-%Y %H:%M:%S"),
                "user-id":user_id,
                "trace_id": trace_id,
                "message": f"Successfully fetched {len(reviews)} reviews"
            })
        else:
            logger.info({
                "date": current_time.strftime("%d-%m-%Y %H:%M:%S"),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No reviews available"
            })
        REQUEST_LATENCY.labels('GET', endpoint,trace_id).observe(time.time() - start_time)
        # return reviews, 200
        return [review.to_dict() for review in reviews], 200

class DelReviewApi(Resource):
    def delete(self, idbook, reviewdate, iduser):
        review_dates = datetime.strptime(reviewdate, '%Y-%m-%d').date()
        message = Review.delete_review(review_dates,iduser,idbook)
        return message,200

class ReviewsAPI(Resource):
    def update(self): #nu il mai folosim
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
        start_time = time.time()
        endpoint = '/api/reviews'
        data = request.get_json()
        review = {
            'reviewdate': datetime.today().date(),
            'iduser': data['iduser'],
            'idbook': data['idbook'],
            'rating': data['rating'],
            'comment': data['comment']
        }
        review_done = Review.create_review(review)
        REQUEST_COUNT.labels('POST', endpoint, 200).inc()
        trace_id = data['trace_id']
        user_id = data['iduser']
        buc_tz = pytz.timezone('Europe/Bucharest')
        current_time = datetime.now(buc_tz)
        if review_done:
            logger.info({
                "date": current_time.strftime("%d-%m-%Y %H:%M:%S"),
                "user-id":user_id,
                "trace_id": trace_id,
                "message": f"Successfully add the review for book {data['idbook']}"
            })
        else:
            logger.info({
                "date": current_time.strftime("%d-%m-%Y %H:%M:%S"),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No review was added"
            })
        REQUEST_LATENCY.labels('POST', endpoint,trace_id).observe(time.time() - start_time)
        return review_done, 200
