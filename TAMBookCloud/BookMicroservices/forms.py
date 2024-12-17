from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

#AUTHOR FORMS

class AuthorViewAllForm(FlaskForm):
    submit = SubmitField('View All Authors')

class AuthorAddForm(FlaskForm):
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    submit = SubmitField('Add Author')

class AuthorViewForm(FlaskForm): #view by IdBook
    firstname = StringField('firstname', validators=[DataRequired()])
    lastname = StringField('lastname', validators=[DataRequired()])
    submit = SubmitField('View Author')

class AuthorDeleteForm(FlaskForm):
    idauthor = StringField('idauthor', validators=[DataRequired()])
    submit = SubmitField('Delete Author')

#BOOK FORMS
class BookAddForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    price = IntegerField('price', validators=[DataRequired()])
    stockstatus = IntegerField('stockstatus', validators=[DataRequired()])
    year = StringField('year', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    publisher = StringField('publisher', validators=[DataRequired()])
    category = StringField('category', validators=[DataRequired()])
    idauthor = StringField('idauthor', validators=[DataRequired()])
    submit = SubmitField('Add Book')

class BookViewForm(FlaskForm): #view by IdBook
    name = StringField('name', validators=[DataRequired()])
    submit = SubmitField('View Book')

class BookViewAllForm(FlaskForm):
    submit = SubmitField('View All Books')

class BookDeleteForm(FlaskForm):
    idbook = StringField('idbook', validators=[DataRequired()])
    submit = SubmitField('Delete Book')

class BookUpdateForm(FlaskForm):
    idbook = StringField('idbook', validators=[DataRequired()])
    stockstatus = IntegerField('stockstatus', validators=[DataRequired()])
    submit = SubmitField('Update Book')