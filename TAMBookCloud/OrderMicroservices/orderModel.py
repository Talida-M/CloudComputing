from flask_sqlalchemy import SQLAlchemy
import uuid
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Order(db.Model):
    __tablename__= 'order'
    idorder = db.Column(db.Integer, primary_key=True)
    iduser = db.Column(db.Integer,  nullable=False)
    totalprice =  db.Column(db.Float, nullable = False)
    address = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    def __init__(self, idorder, iduser, totalprice, address, date):
        self.idorder = idorder
        self.iduser = iduser
        self.totalprice = totalprice
        self.address = address
        self.date = date

    def to_dict(self):
        return {
            'idorder': self.idorder.isoformat(),
            'iduser': self.iduser,
            'date': self.date,
            'totalprice': self.totalprice,
            'address': self.address
        }

    @classmethod
    def create_order(cls,  order_data):
        order = cls( idorder=order_data['idorder'], iduser=order_data['iduser'], totalprice=order_data['totalprice'], address=order_data['address'],  date=order_data['date'])
        db.session.add(order)
        db.session.commit()
        # return order
        return 'Your order was successful created'

    @classmethod
    def get_order_for_user(cls, iduser):
        return cls.query.filter_by(iduser=iduser).all()

    @classmethod
    def get_order(cls, idorder):
        return cls.query.filter_by(idorder=idorder).all()

    @classmethod
    def get_user_order_by_date(cls, iduser, date):
        return cls.query.filter_by(iduser=iduser, date=date).all()


    @classmethod
    def change_order_address(cls, idorder, address):
        order = cls.query.filter_by(idorder=idorder).first()
        if not order:
            return {"error": "Order not found", "status": 404}, 404
        if address is not None:
            order.address = address
        db.session.commit()
        return order

    @classmethod
    def change_order_price(cls, idorder, price):
        order = cls.query.filter_by(idorder=idorder).first()
        if not order:
            return {"error": "Order not found", "status": 404}, 404
        if price is not None:
            order.totalprice = price
        db.session.commit()
        return order
