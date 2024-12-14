from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class ReviewAddForm(FlaskForm):
    idUser = IntegerField('idUser', validators=[DataRequired()])
    idBook = IntegerField('idBook', validators=[DataRequired()])
    rating = IntegerField('rating', validators=[DataRequired()])
    comment = StringField('comment', validators=[DataRequired()])
    submit = SubmitField('Add Review')

class ReviewViewForm(FlaskForm): #view by IdBook
    idBook = IntegerField('idBook', validators=[DataRequired()])
    submit = SubmitField('View Review For Book')

class ReviewDeleteForm(FlaskForm):
    idUser = IntegerField('idUser', validators=[DataRequired()])
    idBook = IntegerField('idBook', validators=[DataRequired()])
    reviewDate = DateField('reviewDate', validators=[DataRequired()])
    submit = SubmitField('Delete Review For Book')

class ReviewUpdateForm(FlaskForm):
    idUser = IntegerField('idUser', validators=[DataRequired()])
    idBook = IntegerField('idBook', validators=[DataRequired()])
    reviewDate = DateField('reviewDate', validators=[DataRequired()])
    rating = IntegerField('rating', validators=[DataRequired()])
    comment = StringField('comment', validators=[DataRequired()])
    submit = SubmitField('Update Review')