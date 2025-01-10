from flask import Flask, render_template, redirect, url_for, flash
from flask_restful import Api
import os

from rabbitmq import send_message_order, connect_rabbitmq
from forms import OrderAddForm, UserOrdersViewForm, OrderViewForm, UserOrderDetailsViewForm, UserOrdersByDateViewForm, \
    OrdeQuantityUpdateForm
from models import db, Order_Detail,Order
from resources import OrderCreateGetAPI, OrderAddingBookOrderAPI, OrderDecrementBookOrderAPI, OrderRemoveBookOrderAPI, \
    SendOrderGetAPI, PendingOrderAPI, OrdersGetAllAPI
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my-secret-pw')
DB_NAME = os.getenv('DB_NAME', 'db')

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SECRET_KEY'] = "SECRET_KEY"

db.init_app(app)

with app.app_context():
    db.create_all()

api.add_resource(OrderCreateGetAPI, '/api/order/<string:iduser>')
api.add_resource(SendOrderGetAPI, '/api/order/send/<string:iduser>')
api.add_resource(OrderAddingBookOrderAPI, '/api/order/add/<string:bookid>/<string:orderid>/<float:price>/<string:name>')#moooooooooooooodiffff
api.add_resource(OrderDecrementBookOrderAPI, '/api/order/decrem/<string:bookid>/<string:orderid>')
api.add_resource(OrderRemoveBookOrderAPI, '/api/order/remove/<string:idbook>/<string:idorder>')
api.add_resource(PendingOrderAPI,'/api/order/pending/<string:iduser>')
api.add_resource(OrdersGetAllAPI,'/api/order/allorders/<string:iduser>')

if __name__ == '__main__':
    app.run(debug=True)