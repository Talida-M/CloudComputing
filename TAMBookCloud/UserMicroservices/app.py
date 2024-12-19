from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
import uuid
import datetime

# Initialize Flask app and extensions


from flask import Flask, render_template, redirect, url_for, make_response
from flask_restful import Api
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token

from resources import Register,Login
from forms import LoginForm,RegisterForm
from userModel import db,User
from datetime import timedelta

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my-secret-pw')
DB_NAME = os.getenv('DB_NAME', 'db')

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)



app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SECRET_KEY'] = "SECRET_KEY"

app.config['JWT_SECRET_KEY'] = '12345678910'
# app.config['JWT_BLACKLIST_ENABLED'] = True
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=2)

db.init_app(app)

with app.app_context():
    db.create_all()
api.add_resource(Register, '/api/register')
api.add_resource(Login, '/api/login')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_route():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = {
            'name': form.name.data,
            'email': form.email.data,
            'password': hashed_password,
        }
        User.add_user(user)
        return redirect(url_for('login_route'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            additional_claims = {
                "iduser": user.iduser
            }
            access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
            response = make_response({'message': 'Login successful'})
            response.set_cookie('access_token', access_token)
            return response
        else:
            return {'message': 'User doesn\'t exist'}
    return render_template('login.html',form=form)

if __name__ == '__main__':
    app.run(debug=True)