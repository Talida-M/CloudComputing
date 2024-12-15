from flask_sqlalchemy import SQLAlchemy
import uuid
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Order_Detail(db.Model):
    __tablename__= 'orderDetail'
    idorder = db.Column(db.Integer,  db.ForeignKey('order.idorder'), primary_key=True)
    order = db.relationship('Order', backref='orderDetail', lazy=True)
    idbook = db.Column(db.Integer,  primary_key=True)
    cantity =  db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable=False)
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
    def create_order_details(cls,  order_data):
        order = cls( idorder=order_data['idorder'], idbook=order_data['idbook'], cantity=order_data['cantity'], price=order_data['price'])
        db.session.add(order)
        db.session.commit()
        return order

    @classmethod
    def get_book_order(cls, idbook, idorder):
        return cls.query.filter_by(idbook=idbook, idorder=idorder).all()

    @classmethod
    def get_books_order(cls, idorder):
        return cls.query.filter_by(idorder=idorder).all()


    @classmethod
    def update_order_cantity(cls, idorder, idbook, cantity):
        order = cls.query.filter_by(idorder=idorder, idbook=idbook).first()
        if not order:
            return {"error": "Order not found", "status": 404}, 404
        if cantity is not None:
            order.cantity = cantity
        db.session.commit()
        return order
