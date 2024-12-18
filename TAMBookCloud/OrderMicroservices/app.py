from flask import Flask, render_template, redirect, url_for, flash
from flask_restful import Api
import os
from forms import OrderAddForm, UserOrdersViewForm, OrderViewForm, UserOrderDetailsViewForm, UserOrdersByDateViewForm, \
    OrdeQuantityUpdateForm
from orderDetailModel import db, Order_Detail
from resources import OrderAPI, OrderDetailAPI, UpdateOrdersDetailsApi

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my-secret-pw')
DB_NAME = os.getenv('DB_NAME', 'db')

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SECRET_KEY'] = "SECRET_KEY"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-order', methods=['GET', 'POST'])
def create_order():
    form = OrderAddForm()

    if form.validate_on_submit():

        data = {
            "iduser": form.iduser.data,
            "address": form.address.data,
            "books": [
                {"idbook": book.idbook.data, "cantity": book.cantity.data, "price": book.price.data}
                for book in form.books.entries
            ]
        }
        flash("Order created successfully!", "success")
        return redirect(url_for('create_order'))

    return render_template('create_order.html', form=form)

@app.route('/view-order', methods=['GET', 'POST'])
def view_order_route():
    form = OrderViewForm()
    if form.validate_on_submit():
        idorder = form.idorder.data
        return redirect(f'/api/order-detail/{idorder}')
    return render_template('view_order.html', form=form)

@app.route('/view-user-orders', methods=['GET', 'POST'])
def view_user_orders_route():
    form = UserOrdersViewForm()
    if form.validate_on_submit():
        iduser = form.iduser.data
        return redirect(f'/api/order/{iduser}')
    return render_template('view_user_orders.html', form=form)

@app.route('/view-user-orders-by-date', methods=['GET', 'POST'])
def view_user_orders_by_date_route():
    form = UserOrdersByDateViewForm()
    if form.validate_on_submit():
        iduser = form.iduser.data
        date = form.date.data.strftime('%Y-%m-%d')
        return redirect(f'/api/orders-by-date/{iduser}/{date}')
    return render_template('view_user_orders_by_date.html', form=form)


@app.route('/view-order-details', methods=['GET', 'POST'])
def view_order_details_route():
    form = UserOrderDetailsViewForm()
    if form.validate_on_submit():
        idorder = form.idorder.data
        return redirect(f'/api/order-details/{idorder}')
    return render_template('view_order_details.html', form=form)

@app.route('/update-order-quantity', methods=['GET', 'POST'])
def update_order_quantity_route():
    form = OrdeQuantityUpdateForm()
    if form.validate_on_submit():
        idorder = form.idorder.data
        idbook = form.idbook.data
        cantity = form.cantity.data

        # Redirect to API for processing
        return redirect(f'/api/update-order?idorder={idorder}&idbook={idbook}&cantity={cantity}')

    return render_template('update_order_quantity.html', form=form)

api.add_resource(OrderAPI, '/api/order/<int:iduser>')
api.add_resource(OrderDetailAPI, '/api/order-detail/<int:idorder>')
api.add_resource(OrderDetailAPI, '/api/order-details/<int:idorder>')
api.add_resource(OrderAPI, '/api/orders-by-date/<int:iduser>/<string:date>')
api.add_resource(UpdateOrdersDetailsApi, '/api/update-order')

if __name__ == '__main__':
    app.run(debug=True)