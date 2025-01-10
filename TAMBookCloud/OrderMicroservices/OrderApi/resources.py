import uuid
from datetime import datetime
from flask import request
from flask_restful import Resource, reqparse
import os

from sqlalchemy.dialects.mysql import DATETIME

from models import Order_Detail,Order
from prometheus_client import Counter, Histogram
import time
from datetime import datetime

import logging
from logging.handlers import SysLogHandler
syslog_host = 'syslog-ng'
syslog_port = 514
logger = logging.getLogger('order_microservice')
logger.setLevel(logging.INFO)

syslog_handler = SysLogHandler(address=(syslog_host, syslog_port))
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)

parser = reqparse.RequestParser()
parser.add_argument('idorder', required=True, help="Order id cannot be blank")
parser.add_argument('idbook', required=True,type=int, help="Book id cannot be blank")
parser.add_argument('cantity', required=True, type=int,help="Cantity cannot be blank")
parser.add_argument('price', required=True,type=int,  help="Price must be a number")

order_parser = reqparse.RequestParser()
order_parser.add_argument('iduser', required=True, help="User ID cannot be blank")
order_parser.add_argument('address', required=True, help="Address is required")
order_parser.add_argument('books', required=True, type=list, location='json',
                          help="Books list is required")


REQUEST_COUNT = Counter(
    'order_microservice_request_count',
    'Request Count for Order Microservice',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'order_microservice_request_latency_seconds',
    'Request Latency for Order Microservice',
    ['method', 'endpoint', 'trace_id'],
    buckets=[0.00001,0.05,0.1,0.25,0.5, 1.0, 2.0, 5.0, 10.0]
)

class OrderCreateGetAPI(Resource):
    def post(self,iduser):
        start_time = time.time()
        endpoint = f'/api/order/{iduser}'
        order = Order.get_or_create_order(iduser)
        REQUEST_COUNT.labels('POST', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "Order created or displayed successfully"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "No order available"
            })
        REQUEST_LATENCY.labels('POST', endpoint, trace_id).observe(time.time() - start_time)
        return order,200

class OrderAddingBookOrderAPI(Resource):
    def post(self,bookid,orderid,price,name):
        # data = request.get_json()
        # bookid = data['idbook']
        # orderid = data['idorder']
        # price = data['price']
        start_time = time.time()
        endpoint = f'/api/order/add/{bookid}/{orderid}/{str(price)}/{name}'
        order = Order.add_book_to_order(bookid,orderid,price,name)
        REQUEST_COUNT.labels('POST', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Book {bookid} successfully added in order {orderid}"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No book added to order"
            })
        REQUEST_LATENCY.labels('POST', endpoint, trace_id).observe(time.time() - start_time)

        return order, 200

class OrderDecrementBookOrderAPI(Resource):
    def delete(self,bookid,orderid): #or put?
        # data = request.get_json()
        # bookid = data['idbook']
        # orderid = data['idorder']
        start_time = time.time()
        endpoint = '/api/order/decrem/' + bookid + orderid
        order = Order.decrement_book_from_order(bookid,orderid)
        REQUEST_COUNT.labels('DELETE', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Pieces of book {bookid} successfully decremented from order {orderid}"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "The book cantity was not decremented"
            })
        REQUEST_LATENCY.labels('DELETE', endpoint, trace_id).observe(time.time() - start_time)
        return order,200

class OrderRemoveBookOrderAPI(Resource):
    def delete(self, idbook,idorder):
        start_time = time.time()
        endpoint = '/api/order/' + idbook + idorder
        order = Order.remove_book_from_order(idbook,idorder)
        REQUEST_COUNT.labels('DELETE', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        user_id = request.headers.get('Id-User', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": f"Book {idbook} removed successfully from order {idorder}"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": user_id,
                "trace_id": trace_id,
                "message": "No book removed"
            })
        REQUEST_LATENCY.labels('DELETE', endpoint, trace_id).observe(time.time() - start_time)

        return order, 200

class SendOrderGetAPI(Resource):
    def put(self, iduser):
        start_time = time.time()
        endpoint = '/api/order/send/' + iduser
        order = Order.sent_order(iduser)
        REQUEST_COUNT.labels('PUT', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "Order successfully sent"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "No order sent"
            })
        REQUEST_LATENCY.labels('PUT', endpoint, trace_id).observe(time.time() - start_time)

        return order, 200

class PendingOrderAPI(Resource):
    def put(self, iduser):
        start_time = time.time()
        endpoint = '/api/order/pending/' + iduser
        order = Order.pending_order(iduser)
        REQUEST_COUNT.labels('PUT', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        if order:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "Order status successfully updated to pending"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "No order status was update to pending"
            })
        REQUEST_LATENCY.labels('PUT', endpoint, trace_id).observe(time.time() - start_time)

        return order, 200

class OrdersGetAllAPI(Resource):
    def get(self, iduser):
        start_time = time.time()
        endpoint = '/api/order/allorders/' + iduser
        orders = Order.get_all_order(iduser)
        REQUEST_COUNT.labels('GET', endpoint, 200).inc()
        trace_id = request.headers.get('X-Trace-ID', 'N/A')
        if orders:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": f"Orders retrieved successfully"
            })
        else:
            logger.info({
                "date": datetime.today().date().isoformat(),
                "user-id": iduser,
                "trace_id": trace_id,
                "message": "No order retrieved"
            })
        REQUEST_LATENCY.labels('GET', endpoint, trace_id).observe(time.time() - start_time)
        return [order.to_dict() for order in orders], 200