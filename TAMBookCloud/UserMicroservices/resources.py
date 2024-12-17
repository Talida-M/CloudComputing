from tkinter.font import names
import uuid
from flask_bcrypt import Bcrypt
from flask_restful import Resource, reqparse
from userModel import User
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



