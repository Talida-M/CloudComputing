from consumer import start_service
from forms import AuthorAddForm, AuthorViewForm, AuthorDeleteForm,AuthorViewAllForm,BookViewAllForm,BookAddForm,BookViewForm,BookUpdateForm,BookDeleteForm
from flask import Flask, render_template, redirect, url_for
from flask_restful import Api
import os
from resources import AuthorsAPI, DelAuthorApi, BookAPI,DelBookApi,AuthorAPI,BooksAPI
# from authorModel import db, Author
# from bookModel import db, Book
from models import db,Author,Book

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

@app.route('/author/add', methods=['GET', 'POST'])
def add_author_route():
    form = AuthorAddForm()
    if form.validate_on_submit():
        author = {
            'lastname': form.lastname.data,
            'firstname': form.firstname.data,
        }
        Author.add_author(author)
        return redirect(f'/api/author/{form.lastname.data}/{form.firstname.data}')
    return render_template('add_author.html', form=form)

@app.route('/author/view', methods=['GET', 'POST'])
def view_author_route():
    form = AuthorViewForm()
    if form.validate_on_submit():
        Author.get_author_by_name(form.lastname.data,form.firstname.data)
        return redirect(f'/api/author/{form.lastname.data}/{form.firstname.data}')
    return render_template('view_author.html', form=form)


@app.route('/author/all', methods=['GET', 'POST'])
def view_all_author_route():
    form = AuthorViewAllForm()
    if form.validate_on_submit():
        Author.get_all_authors()
        return redirect(f'/api/author/')
    return render_template('all_author.html', form=form)

@app.route('/author/delete', methods=['GET','POST'])
def delete_author_route():
    form = AuthorDeleteForm()
    if form.validate_on_submit():
        idauthor = form.idauthor.data
        Author.delete_author_by_id(idauthor)
        return redirect('all')

    return render_template('delete_author.html', form=form)

api.add_resource(AuthorAPI, '/api/author/<string:lastname>/<string:firstname>')
api.add_resource(AuthorsAPI, '/api/author/')
api.add_resource(DelAuthorApi, '/api/author/<string:idauthor>')

####################  BOOKS  ####################

@app.route('/book/add', methods=['GET', 'POST'])
def add_book_route():
    form = BookAddForm()
    if form.validate_on_submit():
        book = {
            'name': form.name.data,
            'price': form.price.data,
            'stockstatus': form.stockstatus.data,
            'year': form.year.data,
            'description': form.description.data,
            'publisher': form.publisher.data,
            'category': form.category.data,
            'idauthor': form.idauthor.data

        }
        Book.add_book(book)
        return redirect(url_for('index'))
        # return redirect(url_for('/api/book/{}'))
    return render_template('add_book.html', form=form)

@app.route('/book/view', methods=['GET', 'POST'])
def view_book_route():
    form = BookViewForm()
    if form.validate_on_submit():
        Book.get_book_by_name(form.name.data)
        return redirect(f'/api/book/{form.name.data}')
    return render_template('view_book.html', form=form)


@app.route('/book/all', methods=['GET', 'POST'])
def view_all_books_route():
    form = BookViewAllForm()
    if form.validate_on_submit():
        Book.get_all_books()
        return redirect(f'/api/book/')
    return render_template('all_books.html', form=form)

@app.route('/book/delete', methods=['GET','POST'])
def delete_book_route():
    form = BookDeleteForm()
    if form.validate_on_submit():
        idbook = form.idbook.data
        Book.delete_book_by_id(idbook)
        return redirect('all')

    return render_template('delete_book.html', form=form)

@app.route('/book/update', methods=['GET','POST'])
def update_book_route():
    form = BookUpdateForm()
    if form.validate_on_submit():
        idbook = form.idbook.data
        stockstatus = form.stockstatus.data
        Book.update_book_stock(idbook,stockstatus)
        return redirect('all')

    return render_template('update_book.html', form=form)

api.add_resource(BooksAPI, '/api/book/')
api.add_resource(BookAPI, '/api/book/<string:name>')
api.add_resource(DelBookApi, '/api/book/<string:idbook>')
# api.add_resource(UpdateBookApi, '/api/book/<string:idbook>/<string:stockstatus>')


if __name__ == '__main__':
    start_service()
    # app.run(debug=True, host="0.0.0.0", port=8000)
    app.run(debug=True)