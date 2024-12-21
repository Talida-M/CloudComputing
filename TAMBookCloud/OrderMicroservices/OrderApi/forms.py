from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms import Form
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

class BookDetailForm(Form):
    idbook = StringField('Book ID', validators=[DataRequired()])
    cantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = IntegerField('Price', validators=[DataRequired(), NumberRange(min=0)])


class OrderAddForm(FlaskForm):
    iduser = StringField('User ID', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    books = FieldList(FormField(BookDetailForm), min_entries=1, label='Books')
    submit = SubmitField('Create Order')

class OrderViewForm(FlaskForm):
    idorder = IntegerField('idorder', validators=[DataRequired()])
    submit = SubmitField('View Order By Id')

class UserOrdersViewForm(FlaskForm):
    iduser = IntegerField('iduser', validators=[DataRequired()])
    submit = SubmitField('View User Orders')

class UserOrdersByDateViewForm(FlaskForm):
    iduser = IntegerField('iduser', validators=[DataRequired()])
    date = DateField('date', validators=[DataRequired()])
    submit = SubmitField('View User Orders from a time period')

class UserOrderDetailsViewForm(FlaskForm):
    idorder = IntegerField('idorder', validators=[DataRequired()])
    submit = SubmitField('View Order Details')

class OrdeQuantityUpdateForm(FlaskForm):
    idorder = IntegerField('idorder', validators=[DataRequired()])
    idbook = IntegerField('idbook', validators=[DataRequired()])
    cantity = IntegerField('cantity', validators=[DataRequired()])
    submit = SubmitField('Update Order Quantity for a book')
