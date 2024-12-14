import sys

from ReviewMicroservices.forms import ReviewAddForm, ReviewViewForm, ReviewDeleteForm, ReviewUpdateForm

sys.path.append('/app')
from flask import Flask, render_template, redirect, url_for
from flask_restful import Api
import os


from .resources import ReviewAPI, ReviewsAPI
from .reviewModel import db, Review

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USERNAME = os.getenv('DB_USERNAME', 'postgresTAM')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'my-secret-pw')
DB_NAME = os.getenv('DB_NAME', 'db')

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SECRET_KEY'] = "SECRET_KEY"

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/review/add', methods=['GET', 'POST'])
def add_review_route():
    form = ReviewAddForm()
    if form.validate_on_submit():
        review = {
            'idUser': form.idUser.data,
            'idBook': form.idBook.data,
            'rating': form.rating.data,
            'comment': form.comment.data,
        }
        Review.create_review(review)
        return redirect(url_for('index'))
    return render_template('add_review.html', form=form)

@app.route('/books/view', methods=['GET', 'POST'])
def view_review_route():
    form = ReviewViewForm()
    if form.validate_on_submit():
        idBook = form.idBook.data
        return redirect(f'/api/review/{idBook}')

    return render_template('view_review.html', form=form)

@app.route('/books/delete', methods=['DELETE'])
def delete_review_route():
    form = ReviewDeleteForm()
    if form.validate_on_submit():
        idUser = form.idUser.data
        reviewDate = form.reviewDate.data
        idBook = form.idBook.data
        return redirect(f'/api/review/{idBook}/{reviewDate}/{idUser}')

    return render_template('view_book.html', form=form)

@app.route('/books/update', methods=['PUT'])
def update_review_route():
    form = ReviewUpdateForm()
    if form.validate_on_submit():

        idUser = form.idUser.data
        reviewDate = form.reviewDate.data
        idBook = form.idBook.data
        comment = form.comment.data
        rating = form.rating.data

        Review.update_review(reviewDate,idUser, idBook, rating, comment)

        return redirect(url_for('index'))
    return render_template('add_book.html', form=form)



api.add_resource(ReviewAPI, '/api/review/<int:idBook>','/api/review/<int:idBook>/<string:reviewDate>/<int:idUser>')
api.add_resource(ReviewsAPI, '/api/reviews')


if __name__ == '__main__':
    app.run(debug=True)