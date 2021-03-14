from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, DateTimeField, SelectMultipleField, FileField, \
    RadioField
from wtforms.validators import (DataRequired,
                                Email,
                                EqualTo,
                                Length)


class AddSession(FlaskForm):
    """Album Edit Form."""
    # title = StringField("Title", validators=[DataRequired()])
    # release = DateField("Released_in", format='%Y', validators=[DataRequired()])
    # img = FileField("Image")
    # parent = SelectField("Parent", coerce=int, choices=[], validators=[DataRequired()])
    # artist = SelectField("Artist", coerce=int, choices=[], validators=[DataRequired()])
    # genres = SelectMultipleField("Genders", coerce=int, choices=[], validators=[DataRequired()])
    day =  DateField("Jour", validators=[DataRequired()])
    timeB = DateTimeField("Heure début", format='%H:%M', validators=[DataRequired()])
    timeE = DateTimeField("Heure fin", format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Sauvegarder')