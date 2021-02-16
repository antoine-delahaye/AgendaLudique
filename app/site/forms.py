# app/site/forms.py

from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import PasswordField, StringField, SubmitField, SelectField, BooleanField, RadioField
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


class GamesSimpleSearchForm(FlaskForm):
    games_hint = StringField("Nom du jeu", id='search-input', render_kw={
        'class': 'form-control',
        'placeholder': 'Rechercher des jeux grâce à leurs noms',
        'aria-describedby': 'search-buttons'
    })
    display_known_games = BooleanField('Afficher uniquement les jeux que vous connaissez')
    display_noted_games = BooleanField('Afficher uniquement les jeux notés')
    display_wished_games = BooleanField('Afficher uniquement les jeux souhaités')
    display_owned_games = BooleanField('Afficher uniquement les jeux possédés')
    display_search_parameter = RadioField('Catégories de la recherche : ', choices=
        [('KNOWN',"Afficher uniquement les jeux que vous connaissez"),
            ('NOTED',"Afficher uniquement les jeux notés"),
            ('WISHED',"Afficher uniquement les jeux souhaités"),
            ('OWNED',"Afficher uniquement les jeux possédés")
        ])


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