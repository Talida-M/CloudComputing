from typing import Optional

from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'

    iduser = db.Column(db.String, primary_key = True)
    name =  db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique = True, nullable=False)
    password =  db.Column(db.String(255), nullable=False)


    def __init__(self, iduser, email, password,name):
        self.iduser = iduser
        self.email = email
        self.password = password
        self.name = name

    @classmethod
    def find_by_email(cls, email)-> Optional["User"]:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_all_users(cls):
        users = cls.query.all()
        return [user.to_dict() for user in users]

    def to_dict(self):
        return {
            'iduser': self.iduser,
            'name':self.name,
            'email':self.email
        }

    @classmethod
    def add_user(cls, user_data):
        user = User(
                iduser = uuid.uuid4(),
                email= user_data['email'],
                password = user_data['password'],
                name = user_data['name'])

        db.session.add(user)
        db.session.commit()
        return 'Your registration was successful'

    @classmethod
    def login(cls, user_data):
        email = user_data['email']
        password = user_data['password']

        login = User.query.filter_by(email=email, password=password).first()
        if login is not None:
            return 0 #the login is successfull
        else:
            return 1