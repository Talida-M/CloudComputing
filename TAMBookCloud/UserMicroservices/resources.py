import uuid
from flask import request
from flask_bcrypt import Bcrypt
from flask_restful import Resource, reqparse
from userModel import User, db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
bcrypt = Bcrypt()
parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help="name cannot be blank")
parser.add_argument('email', required=True, help="email cannot be blank")
parser.add_argument('password', required=True,help="password cannot be blank")

class UserRegister(Resource):
    def post(self):
        data = parser.parse_args()
        email = data['email']

        if User.find_by_email(email):
            return {'message': 'Already exists'}

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            'iduser': uuid.uuid4(),
            'name': data['name'],
            'email': email,
            'password': hashed_password,
        }
        try:
            User.add_user(user)
            name = data['name']
            return {'message': f' {name} was created'}

        except:
            return {'message': 'Unsuccessful register'}, 500



class Register(Resource):
    def post(self):
        data = request.get_json()
        #data = parser.parse_args()
        if not data or not data.get('email') or not data.get('password') or not data.get('name'):
            return {'message': 'Missing required fields'}, 400

        if User.find_by_email(data['email']):
            return {'message': 'User with this email already exists'}, 409

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        # Create a new user
        new_user = User(
            iduser = uuid.uuid4(),
            name=data['name'],
            email=data['email'],
            password=hashed_password#data['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return {'message': 'User registered successfully', 'user': new_user.to_dict()}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return {'message': 'Missing email or password'}, 400

        user = User.find_by_email(data['email'])
        if user and bcrypt.check_password_hash(user.password, data['password']):
            # Create JWT token
            additional_claims = {
                "iduser": user.iduser
            }
            access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
            return {'message': 'Login successful', 'access_token': access_token}, 200

        return {'message': 'Invalid email or password'}, 401





class UserLogin(Resource):

    def post(self):

        data = parser.parse_args()
        email = data['email']

        current_user = User.find_by_email(email)
        if not current_user:
            return {'message': 'User doesn\'t exist'}

        # user exists, comparing password and hash
        if bcrypt.generate_password_hash(data['password'], current_user.password):

            #generating access token and refresh token
            additional_claims = {
                    "iduser": data['iduser']
                }
            #
            # Create token with additional claims
            access_token = create_access_token(identity=email, additional_claims=additional_claims)
            #access_token = create_access_token(identity=email)
            #refresh_token = create_refresh_token(identity=email)

            return {

                'message': f'Log in with {email}',

                'access_token': access_token,

                # 'refresh_token': refresh_token
            }

        else:

            return {'message': "Unsuccessful login"}



