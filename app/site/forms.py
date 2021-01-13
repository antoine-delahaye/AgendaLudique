# app/site/forms.py

from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import PasswordField, StringField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class UpdateInformationForm(FlaskForm):
    """
    Form for users to update our informations
    """
    username = StringField('Pseudo', validators=[DataRequired()], render_kw={'placeholder': 'Pseudo'})
    first_name = StringField('Prénom', validators=[DataRequired()], render_kw={'placeholder': 'Prénom'})
    last_name = StringField('Nom', validators=[DataRequired()], render_kw={'placeholder': 'Nom'})
    password = PasswordField('Mot de passe', validators=[DataRequired(), EqualTo('confirm_password')],
                             render_kw={'placeholder': 'Mot de passe'})
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[DataRequired()],
                                     render_kw={'placeholder': 'Confirmer le mot de passe'})
    profile_picture = StringField('Photo de profile', validators=[DataRequired()],
                                  render_kw={'placeholder': 'URL de la photo de profile'})
    submit = SubmitField('Mettre à jour')


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


class UsersSearchForm(FlaskForm):
    """
    Form to search users
    """
    username_hint = StringField("Nom de l'utilisateur", id='search-input', render_kw={
        'class': 'form-control',
        'placeholder': 'Rechercher un utilisateur grâce à son nom',
        'aria-describedby': 'search-buttons'
    })
    display_favorites_players_only = BooleanField('Afficher uniquement les joueurs favoris')
    display_masked_players = BooleanField('Afficher les joueurs masqués')