from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
import uuid

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import backref
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Order(db.Model):
    __tablename__= 'orders'
    idorder = db.Column(db.String, primary_key=True)
    iduser = db.Column(db.String,  nullable=False)
    status = db.Column(db.String(255),nullable = False)
    totalprice =  db.Column(db.Float, nullable = False)
    # address = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

    order_orderdetails = db.relationship('Order_Detail',backref='orders',lazy = 'select')#order.orders acceseaza toate OrderDetails ale orderului

    def __init__(self, idorder, iduser, status, totalprice, date):
        self.idorder = idorder
        self.iduser = iduser
        self.status = status
        self.totalprice = totalprice
        self.date = date

    def to_dict(self):
        order_details = [detail.to_dict() for detail in self.order_orderdetails]
        return {
            'idorder': self.idorder,
            'iduser': self.iduser,
            'status':self.status,
            'date':  self.date.strftime('%Y-%m-%d'),
            'totalprice': self.totalprice,
            'order_orderdetails': order_details  # Access related Order_Details
        }


    @classmethod
    def get_all_order(self,iduser):
        orders = Order.query.filter(Order.iduser == iduser,Order.status.in_(["pending","success"])).order_by(Order.date.desc()).all()
        return orders

    @classmethod
    def sent_order(self,iduser):
        order = Order.query.filter_by(iduser=iduser,status="pending").order_by(Order.date.desc()).first()
        #cand facem cu rabbitmq - nu mai e nevoie de order.status si db.session.commit
        # send_message(order)
        # send_message_to_queue_order(order)
        order.status = "success"
        db.session.commit()
        return order.to_dict()

    # def send_message_to_queue_order(data):
    #     channel = connect_rabbitmq()
    #     send_message_order(channel, 'order_queue', data)
    #     channel.close()

    @classmethod
    def pending_order(self, iduser):
        order = Order.query.filter_by(iduser=iduser, status="start").order_by(Order.date.desc()).first()
        if order is None:
            return "No order found for this user"
        order.status = "pending"
        db.session.commit()
        return order.to_dict()

    @classmethod
    def get_or_create_order(cls,iduser):
        # order = Order.query.filter_by(iduser=iduser).first()
        order = Order.query.filter_by(iduser=iduser,status="start").order_by(Order.date.desc()).first()

        if not order:
            order = Order(
                idorder=uuid.uuid4(),
                iduser=iduser,
                status="start",
                date=datetime.today().date(),
                totalprice=0.0
            )
            db.session.add(order)
            db.session.commit()

        return order.to_dict()

    @classmethod
    def add_book_to_order(cls,book_id, order_id, book_price):
        try:
            #Find the order by ID
            order = Order.query.filter_by(idorder=order_id).first()
        except NoResultFound:
            raise ValueError("Does not exist an order with this id")

        # Add the book to the order and get the book price
        book_price_in_order = Order_Detail.add_book_to_order_details(book_id,order_id,book_price)

        # Update the order's total price
        order.totalprice += book_price_in_order
        db.session.commit()
        return order.to_dict()

    @classmethod
    def remove_book_from_order(cls, book_id, order_id):
        try:
            # Find the order by ID
            order = Order.query.filter_by(idorder=order_id).first()
        except NoResultFound:
            raise ValueError("Does not exist an order with this id")

        book_price_in_order = Order_Detail.remove_book_from_order_details(book_id,order_id)
        order.totalprice -=book_price_in_order
        db.session.commit()
        return order.to_dict()

    @classmethod
    def decrement_book_from_order(cls, book_id, order_id):
        try:
            # Find the order by ID
            order = Order.query.filter_by(idorder=order_id).first()
        except NoResultFound:
            raise ValueError("Does not exist an order with this id")

        book_price_in_order = Order_Detail.decrement_book_from_order_details(book_id,order_id)
        order.totalprice -=book_price_in_order
        db.session.commit()
        return order.to_dict()


    # @classmethod
    # def create_order_new(cls, order_data):
    #     order = Order(
    #         idorder=uuid.uuid4(),
    #         iduser=order_data['iduser'],
    #         status="pending",
    #         date=datetime.today().date(),
    #         totalprice=order_data['totalprice'],
    #     )
    #     db.session.add(order)
    #     db.session.commit()
    #     return order.to_dict()

    # @classmethod
    # def create_order(cls,  order_data):
    #     order = cls( idorder=order_data['idorder'],status=order_data['status'], iduser=order_data['iduser'], totalprice=order_data['totalprice'], date=order_data['date'])
    #     db.session.add(order)
    #     db.session.commit()
    #     # return order
    #     return 'Your order was successful created'
    #
    # @classmethod
    # def get_order_for_user(cls, iduser):
    #     return cls.query.filter_by(iduser=iduser).all()
    #
    # @classmethod
    # def get_order(cls, idorder):
    #     return cls.query.filter_by(idorder=idorder).all()
    #
    # @classmethod
    # def get_user_order_by_date(cls, iduser, date):
    #     return cls.query.filter_by(iduser=iduser, date=date).all()
    #
    #
    # @classmethod
    # def change_order_address(cls, idorder, address):
    #     order = cls.query.filter_by(idorder=idorder).first()
    #     if not order:
    #         return {"error": "Order not found", "status": 404}, 404
    #     if address is not None:
    #         order.address = address
    #     db.session.commit()
    #     return order
    #
    # @classmethod
    # def change_order_price(cls, idorder, price):
    #     order = cls.query.filter_by(idorder=idorder).first()
    #     if not order:
    #         return {"error": "Order not found", "status": 404}, 404
    #     if price is not None:
    #         order.totalprice = price
    #     db.session.commit()
    #     return order


class Order_Detail(db.Model):
    __tablename__= 'orderdetails'
    idorder = db.Column(db.String,  db.ForeignKey('orders.idorder'), nullable=False)
    idbook = db.Column(db.String,  nullable=False)
    cantity =  db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('idorder', 'idbook'),
    )

    def __init__(self, idorder, idbook, cantity, price):
        self.idorder = idorder
        self.idbook = idbook
        self.cantity = cantity
        self.price = price

    def to_dict(self):
        return {
            'idorder': self.idorder,
            'idbook': self.idbook,
            'cantity': self.cantity,
            'price': self.price,
        }

    @classmethod
    def add_book_to_order_details(cls,book_id, order_id,book_price):

        # Verify if book is in the order
        book_order = Order_Detail.query.filter_by(idbook=book_id,idorder=order_id).first()

        if not book_order:
            # Create a new BookOrder entry if the book is not in the order
            book_order = Order_Detail(
                cantity=1,
                price=book_price,
                idbook=book_id,
                idorder=order_id
            )
            db.session.add(book_order)
        else:
            # Increment the number of copies if the book already exists in the order
            book_order.cantity += 1

        db.session.commit()

        return book_order.price

    @classmethod
    def remove_book_from_order_details(cls,book_id, order_id):

        # Verify if book is in the order
        book_order = Order_Detail.query.filter_by(idbook=book_id,idorder=order_id).first()
        if book_order:
            db.session.delete(book_order)
            db.session.commit()
            return book_order.price * book_order.cantity
        else:
            raise ValueError(f"No order detail found")

    @classmethod
    def decrement_book_from_order_details(cls,book_id,order_id):
        book_order = Order_Detail.query.filter_by(idbook=book_id, idorder=order_id).first()
        if not book_order:
            raise ValueError(f"No order detail found")
        if book_order.cantity > 1:
            # Decrement the number of copies
            book_order.cantity -= 1
            db.session.commit()
        else:
            # Remove the book from the order if it's the last copy
            db.session.delete(book_order)
            db.session.commit()

        return book_order.price





#########
    # @classmethod
    # def create_order_details(cls,  order_data):
    #     order = cls( idorder=order_data['idorder'], idbook=order_data['idbook'], cantity=order_data['cantity'], price=order_data['price'])
    #     db.session.add(order)
    #     db.session.commit()
    #     return order
    #
    #
    # @classmethod
    # def create_order_details_new(cls,  order_data):
    #     orderdetails = Order_Detail(
    #         idorder= order_data['idorder'],
    #         idbook= order_data['idbook'],
    #         cantity=order_data['cantity'],
    #         price = order_data['price']
    #     )
    #
    #     db.session.add(orderdetails)
    #     db.session.commit()
    #     return orderdetails.to_dict()
    #
    #
    # @classmethod
    # def get_book_order(cls, idbook, idorder):
    #     return cls.query.filter_by(idbook=idbook, idorder=idorder).all()
    #
    # @classmethod
    # def get_books_order(cls, idorder):
    #     return cls.query.filter_by(idorder=idorder).all()
    #
    #
    # @classmethod
    # def update_order_cantity(cls, idorder, idbook, cantity):
    #     order = cls.query.filter_by(idorder=idorder, idbook=idbook).first()
    #     if not order:
    #         return {"error": "Order not found", "status": 404}, 404
    #     if cantity is not None:
    #         order.cantity = cantity
    #     db.session.commit()
    #     return order
