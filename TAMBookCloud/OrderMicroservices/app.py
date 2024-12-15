# from forms import ReviewAddForm, ReviewViewForm, ReviewDeleteForm, ReviewUpdateForm
from flask import Flask, render_template, redirect, url_for
from flask_restful import Api
import os
from resources import OrderDetailAPI, OrdersDetailsAPI, UpdateOrdersDetailsApi
from orderDetailModel import db, Order_Detail

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

@app.route('/orderDetails/add', methods=['GET', 'POST'])
def add_orderDetails_route():
    form = ReviewAddForm()
    if form.validate_on_submit():
        review = {
            'iduser': form.iduser.data,
            'idbook': form.idbook.data,
            'rating': form.rating.data,
            'comment': form.comment.data,
        }
        Review.create_review(review)
        return redirect(url_for('index'))
    return render_template('add_review.html', form=form)

@app.route('/review/view', methods=['GET', 'POST'])
def view_review_route():
    form = ReviewViewForm()
    if form.validate_on_submit():
        idbook = form.idbook.data
        return redirect(f'/api/review/{idbook}')

    return render_template('view_review.html', form=form)

@app.route('/review/delete', methods=['GET','POST'])
def delete_review_route():
    form = ReviewDeleteForm()
    if form.validate_on_submit():
        iduser = form.iduser.data
        reviewdate = form.reviewdate.data
        idbook = form.idbook.data

        reviewdate_str = reviewdate.strftime('%Y-%m-%d')
        return redirect(f'/api/review/{idbook}/{reviewdate_str}/{iduser}')

    return render_template('delete_review.html', form=form)

@app.route('/review/update', methods=['GET', 'POST'])
def update_review_route():
    form = ReviewUpdateForm()

    if form.validate_on_submit():
        iduser = form.iduser.data
        idbook = form.idbook.data
        reviewdate = form.reviewdate.data
        comment = form.comment.data
        rating = form.rating.data

        updated_review = Review.update_review(reviewdate, iduser, idbook, rating, comment)

        if updated_review:
            return redirect(url_for('index')) #success
        else:
            return "Review not found for the specified book, user, and review date", 404
    return render_template('update_review.html', form=form)

api.add_resource(ReviewAPI, '/api/review/<int:idbook>')
api.add_resource(DelReviewApi, '/api/review/<int:idbook>/<string:reviewdate>/<int:iduser>')
api.add_resource(ReviewsAPI, '/api/reviews')


if __name__ == '__main__':
    app.run(debug=True)