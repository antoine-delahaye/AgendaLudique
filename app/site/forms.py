# app/site/forms.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

from app.models import User


class UpdateProfilForm(FlaskForm):
    """
    Form for users to update our profil
    """
    email = StringField('Adresse électronique', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Adresse électronique', 'disabled': 'disabled'})
    username = StringField('Pseudo', validators=[DataRequired()], render_kw={'placeholder': 'Pseudo'})
    first_name = StringField('Prénom', validators=[DataRequired()], render_kw={'placeholder': 'Prénom'})
    last_name = StringField('Nom', validators=[DataRequired()], render_kw={'placeholder': 'Nom'})
    password = PasswordField('Mot de passe', validators=[DataRequired(), EqualTo('confirm_password')],
                             render_kw={'placeholder': 'Mot de passe'})
    confirm_password = PasswordField('Confirmer le mot de passe',
                                     render_kw={'placeholder': 'Confirmer le mot de passe'})
    profil_picture = StringField('Photo de profile', render_kw={'placeholder': 'URL de la photo de profile'})
    submit = SubmitField('Mettre à jour')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Pseudo déjà utilisé')


class GamesSearchForm(FlaskForm):
    """
    Form for search games
    """
    title = SelectField('Nom du jeu', choices=[])
    years = SelectField('Années de sortie', choices=[])
    min_players = SelectField('Joueurs minimum', choices=[])
    max_players = SelectField('Joueurs maximum', choices=[])
    min_playtime = SelectField('Durée minimale', choices=[])
    max_playtime = SelectField('Durée maximale', choices=[])
    submit = SubmitField('Rechercher')
