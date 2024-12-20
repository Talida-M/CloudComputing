from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class ReviewAddForm(FlaskForm):
    iduser = StringField('iduser', validators=[DataRequired()])
    idbook = StringField('idbook', validators=[DataRequired()])
    rating = IntegerField('rating', validators=[DataRequired()])
    comment = StringField('comment', validators=[DataRequired()])
    submit = SubmitField('Add Review')

class ReviewViewForm(FlaskForm): #view by IdBook
    idbook = StringField('idbook', validators=[DataRequired()])
    submit = SubmitField('View Review For Book')

class ReviewDeleteForm(FlaskForm):
    iduser = StringField('iduser', validators=[DataRequired()])
    idbook = StringField('idbook', validators=[DataRequired()])
    reviewdate = DateField('reviewdate', validators=[DataRequired()])
    submit = SubmitField('Delete Review For Book')

class ReviewUpdateForm(FlaskForm):
    iduser = StringField('iduser', validators=[DataRequired()])
    idbook = StringField('idbook', validators=[DataRequired()])
    reviewdate = DateField('reviewdate', validators=[DataRequired()])
    rating = IntegerField('rating', validators=[DataRequired()])
    comment = StringField('comment', validators=[DataRequired()])
    submit = SubmitField('Update Review')