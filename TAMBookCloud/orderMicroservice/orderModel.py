from flask_sqlalchemy import SQLAlchemy
import uuid
from wtforms.validators import email
from flask import Flask, request, jsonify
db = SQLAlchemy()

class Order(db.Model):
    __tablename__= 'order'
    idOrder = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer, nullable=False)
    totalPrice =  db.Column(db.Float, nullable = False)
    address = db.Column(db.String(255), nullable=False)
    status =  db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    def __init__(self, idOrder, idUser, totalPrice, address, status, date):
        self.idOrder = idOrder
        self.idUser = idUser
        self.totalPrice = totalPrice
        self.address = address
        self.status = status
        self.date = date

    def to_dict(self):
        return {
            'idOrder': self.idOrder.isoformat(),
            'idUser': self.idUser,
            'date': self.date,
            'totalPrice': self.totalPrice,
            'status': self.status,
            'address': self.address
        }

    @classmethod
    def create_order(cls,  idUser, totalPrice, address, status,  date):
        order = cls( idOrder=uuid.uuid4(), idUser=idUser, totalPrice=totalPrice, address=address, status=status, date=date)
        db.session.add(order)
        db.session.commit()
        return order

    @classmethod
    def get_order_for_user(cls, idUser):
        return cls.query.filter_by(idUser=idUser).all()

    @classmethod
    def get_order(cls, idOrder):
        return cls.query.filter_by(idOrder=idOrder).all()

    @classmethod
    def get_user_order_by_date(cls, idUser, date):
        return cls.query.filter_by(idUser=idUser, date=date).all()

    @classmethod
    def update_order_status(cls, idOrder, status):
        order = cls.query.filter_by(idOrder=idOrder).first()
        if not order:
            return None
        if status is not None:
            order.status = status
        db.session.commit()
        return order

    @classmethod
    def change_order_address(cls, idOrder, address):
        order = cls.query.filter_by(idOrder=idOrder).first()
        if not order:
            return None
        if address is not None:
            order.address = address
        db.session.commit()
        return order
