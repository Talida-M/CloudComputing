import uuid
from datetime import datetime

from flask_restful import Resource, reqparse
import os

from sqlalchemy.dialects.mysql import DATETIME

from orderDetailModel import  Order_Detail
from orderModel import  Order
parser = reqparse.RequestParser()
parser.add_argument('idorder', required=True, help="Order id cannot be blank")
parser.add_argument('idbook', required=True,type=int, help="Book id cannot be blank")
parser.add_argument('cantity', required=True, type=int,help="Cantity cannot be blank")
parser.add_argument('price', required=True,type=int,  help="Price must be a number")

order_parser = reqparse.RequestParser()
order_parser.add_argument('iduser', required=True, help="User ID cannot be blank")
order_parser.add_argument('address', required=True, help="Address is required")
order_parser.add_argument('books', required=True, type=list, location='json',
                          help="Books list is required")  # Expect a list of books

class OrderDetailAPI(Resource):
    def get_params(self, idorder, idbook):
        order = Order_Detail.get_book_order(idbook, idorder)

        if not order:
            return {"error": "Order not found.", "status": 404}, 404

        return {"data": [order.to_dict()]}, 200

    def get_param(self, idorder):
        orders = Order_Detail.get_books_order(idorder)

        if not orders:
            return {"error": "No orders found.", "status": 404}, 404

        result = [order.to_dict() for order in orders]
        return {"data": result}, 200

class UpdateOrdersDetailsApi(Resource):
    def update(self):
        args = parser.parse_args()
        idorder = args['idorder']
        idbook = args['idbook']
        cantity = args.get('cantity')
        if cantity is not None:
            response = Order_Detail.update_order_cantity(idorder, idbook, cantity)
        else:
            return {"error": "No update parameters provided.", "status": 400}, 400

        return {"message": "Order updated successfully.", "data": response.to_dict()}, 200

class OrdersAPI(Resource):

    def post(self):
        args = order_parser.parse_args()
        books = args['books']
        new_order = {
            'idorder': uuid.uuid4(),
            'iduser': args['iduser'],
            'totalprice': 0,
            'address': args['address'],
            'date': datetime.today().date() }

        order_done = Order.create_order(new_order)

        if not books or not isinstance(books, list):
            return {"error": "Books list must be provided and non-empty"}, 400

        idorder = new_order['idorder']
        created_order_details = []
        totalPrice = 0
        for book in books:
            try:
                idbook = book['idbook']
                cantity = book['cantity']
                price = book['price']

                order_detail = {
                    'idorder': idorder,
                    'idbook': idbook,
                    'cantity': cantity,
                    'price': price,
                }
                totalPrice  += order_detail['price']
                created_detail = Order_Detail.create_order_details(order_detail)
                created_order_details.append(created_detail.to_dict())
            except KeyError as e:
                return {"error": f"Missing field in book details: {str(e)}"}, 400
        updated_order = Order.change_order_price(idorder, totalPrice)
        return {
                   "message": "Order and details created successfully",
                   "order": updated_order.to_dict(),
                   "order_details": created_order_details
               }, 201
        # args = parser.parse_args()
        # order = {
        #     'idorder': args['idorder'],
        #     'idbook': args['idbook'],
        #     'cantity': args['cantity'],
        #     'price': args['price'],
        #     'discount': args['discount']
        # }
        # basket_done = Order_Detail.create_order_details(order)
        # return {'Order':basket_done['idorder']}, 201