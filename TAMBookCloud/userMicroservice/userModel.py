from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.testing.suite.test_reflection import users
from rabbitmq import connect_rabbitmq, send_message
import uuid
import bcrypt
from wtforms.validators import email

db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'users'

    idUser = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(255), nullable=False)
    password =  db.Column(db.String(255), nullable=False)
    name =  db.Column(db.String(255), nullable=False)
    gender =  db.Column(db.String(2), nullable=False)

    def __init__(self, idUser, email, password,name,gender):
        self.idUser = idUser
        self.email = email
        self.password = password
        self.name = name
        self.gender = gender

    @classmethod
    def get_all_users(cls):
        users = cls.query.all()
        return [user.to_dict() for user in users]
    def to_dict(self):
        return {
            'idUser': self.idUser,
            'name':self.name,
            'gender':self.gender
        }

    @classmethod
    def register(cls, user_data):
        bytes_password =  user_data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes_password, salt)
        user = {
                'idUser': uuid.uuid4(),
                'email': user_data['email'],
                'password': hash,
                'name': user_data['name'],
                'gender':user_data['gender']
        }
        send_message_to_queue(user)
        # userul = User(
        #     idUser= uuid.uuid4(),
        #     email=user_data['email'],
        #     password=hash,
        #     name=user_data['name'],
        #     gender=user_data['gender'])
        # db.session.add(userul)
        # db.session.commit()
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

def send_message_to_queue(user_data):
    channel = connect_rabbitmq()
    send_message(channel, 'user_queue', user_data)
    channel.close()