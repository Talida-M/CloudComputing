from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
import uuid

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import backref
from wtforms.validators import email
from flask import Flask, request, jsonify

from rabbitmq import connect_rabbitmq, send_message_order

db = SQLAlchemy()

class Order(db.Model):
    __tablename__= 'orders'
    idorder = db.Column(db.String, primary_key=True)
    iduser = db.Column(db.String,  nullable=False)
    status = db.Column(db.String(255),nullable = False)
    totalprice =  db.Column(db.Float, nullable = False)
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
        order_data = {
            "idorder": order.idorder,
            "iduser": order.iduser,
            "status": order.status,
            "totalprice":order.totalprice,
        }

        send_message_to_queue_order(order_data)

        # order.status = "success" astea se fac on rabbit cand merge
        # db.session.commit()
        return order.to_dict()

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
    def add_book_to_order(cls,book_id, order_id, book_price, name):
        try:
            order = Order.query.filter_by(idorder=order_id).first()
        except NoResultFound:
            raise ValueError("Does not exist an order with this id")

        book_price_in_order = Order_Detail.add_book_to_order_details(book_id,order_id,book_price,name)
        order.totalprice += book_price_in_order
        db.session.commit()
        return order.to_dict()

    @classmethod
    def remove_book_from_order(cls, book_id, order_id):
        try:
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
            order = Order.query.filter_by(idorder=order_id).first()
        except NoResultFound:
            raise ValueError("Does not exist an order with this id")

        book_price_in_order = Order_Detail.decrement_book_from_order_details(book_id,order_id)
        order.totalprice -=book_price_in_order
        db.session.commit()
        return order.to_dict()

class Order_Detail(db.Model):
    __tablename__= 'orderdetails'
    idorder = db.Column(db.String,  db.ForeignKey('orders.idorder'), nullable=False)
    idbook = db.Column(db.String,  nullable=False)
    cantity =  db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable=False)
    name = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('idorder', 'idbook'),
    )

    def __init__(self, idorder, idbook, cantity, price, name):
        self.idorder = idorder
        self.idbook = idbook
        self.cantity = cantity
        self.price = price
        self.name = name

    def to_dict(self):
        return {
            'idorder': self.idorder,
            'idbook': self.idbook,
            'cantity': self.cantity,
            'price': self.price,
            'name': self.name
        }

    @classmethod
    def add_book_to_order_details(cls,book_id, order_id,book_price, name):
        book_order = Order_Detail.query.filter_by(idbook=book_id,idorder=order_id).first()

        if not book_order:
            book_order = Order_Detail(
                cantity=1,
                price=book_price,
                idbook=book_id,
                idorder=order_id,
                name = name
            )
            db.session.add(book_order)
        else:
            book_order.cantity += 1

        db.session.commit()

        return book_order.price

    @classmethod
    def remove_book_from_order_details(cls,book_id, order_id):
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
            book_order.cantity -= 1
            db.session.commit()
        else:
            db.session.delete(book_order)
            db.session.commit()

        return book_order.price

def send_message_to_queue_order(data):
    channel = connect_rabbitmq()
    send_message_order(channel, 'order_queue', data)
    channel.close()
