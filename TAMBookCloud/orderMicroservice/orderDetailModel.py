from flask_sqlalchemy import SQLAlchemy
import uuid
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Order_Detail(db.Model):
    __tablename__= 'orderDetail'
    idOrder = db.Column(db.Integer, primary_key=True)
    idBook = db.Column(db.Integer, primary_key=True)
    cantity =  db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    def __init__(self, idOrder, idBook, cantity, price, discount):
        self.idOrder = idOrder
        self.idBook = idBook
        self.cantity = cantity
        self.price = price
        self.discount = discount

    def to_dict(self):
        return {
            'idOrder': self.idOrder,
            'idBook': self.idBook,
            'cantity': self.cantity,
            'price': self.price,
            'discount': self.discount,
        }

    @classmethod
    def create_order_details(cls,  idOrder, idBook, cantity, price, discount):
        order = cls( idOrder=idOrder, idBook=idBook, cantity=cantity, price=price, discount=discount)
        db.session.add(order)
        db.session.commit()
        return order

    @classmethod
    def get_book_order(cls, idBook, idOrder):
        return cls.query.filter_by(idBook=idBook, idOrder=idOrder).all()

    def get_books_order(cls, idOrder):
        return cls.query.filter_by(idOrder=idOrder).all()


    @classmethod
    def update_order_cantity(cls, idOrder, idBook, cantity):
        order = cls.query.filter_by(idOrder=idOrder, idBook=idBook).first()
        if not order:
            return None
        if cantity is not None:
            order.cantity = cantity
        db.session.commit()
        return order

    @classmethod
    def change_order_discount(cls, idOrder, idBook, discount):
        order = cls.query.filter_by(idOrder=idOrder, idBook=idBook).first()
        if not order:
            return None
        if discount is not None:
            order.discount = discount
        db.session.commit()
        return order
