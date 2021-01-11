# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import User


class LoginForm(FlaskForm):
    """
    Form for users to sign in
    """
    email = StringField('Adresse électronique', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Adresse électronique'})
    password = PasswordField('Mot de passe', validators=[DataRequired()], render_kw={'placeholder': 'Mot de passe'})
    submit = SubmitField('Connexion')


class RegistrationForm(FlaskForm):
    """
    Form for users to sign up
    """
    email = StringField('Adresse électronique', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Adresse électronique'})
    username = StringField('Pseudo', validators=[DataRequired()], render_kw={'placeholder': 'Pseudo'})
    first_name = StringField('Prénom', validators=[DataRequired()], render_kw={'placeholder': 'Prénom'})
    last_name = StringField('Nom', validators=[DataRequired()], render_kw={'placeholder': 'Nom'})
    password = PasswordField('Mot de passe', validators=[DataRequired(), EqualTo('confirm_password')],
                             render_kw={'placeholder': 'Mot de passe'})
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     render_kw={'placeholder': 'Confirmer le mot de passe'})
    submit = SubmitField('Inscription')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Adresse électronique déjà utilisée')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Pseudo déjà utilisé')
