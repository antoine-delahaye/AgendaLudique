# app/site/forms.py

from flask_wtf import FlaskForm
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
    use_gravatar = BooleanField('Utiliser Gravatar')
    profile_picture = StringField('Photo de profile', validators=[DataRequired()],
                                  render_kw={'placeholder': 'URL de la photo de profile'})
    submit = SubmitField('Mettre à jour')


class GamesSimpleSearchForm(FlaskForm):
    games_hint = StringField("Nom du jeu", id='search-input', render_kw={
        'class': 'form-control',
        'placeholder': 'Rechercher des jeux en fonction du ...',
        'aria-describedby': 'search-buttons'
    })
    display_search_type = SelectField('Type', choices=[('title',"Nom"),('genre',"Genre"),('year',"Année")])
    display_search_parameter = RadioField('Catégorie de la recherche : ', choices=
        [(None, "Afficher tout les jeux"),
            ('KNOWN',"Afficher uniquement les jeux que vous connaissez"),
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


class AddGameForm(FlaskForm):
    """
    Form for add game
    """
    title = StringField('Titre', validators=[DataRequired()], render_kw={'placeholder': 'Titre'})
    years = StringField('Année de sortie', validators=[DataRequired()], render_kw={'placeholder': 'Année de sortie'})
    min_players = StringField('Joueurs minimum', validators=[DataRequired()],
                              render_kw={'placeholder': 'Joueurs minimum'})
    max_players = StringField('Joueurs maximum', validators=[DataRequired()],
                              render_kw={'placeholder': 'Joueurs maximum'})
    min_playtime = StringField('Durée minimale (en minutes)', validators=[DataRequired()],
                               render_kw={'placeholder': 'Durée minimale'})
    image = StringField('Illustration', validators=[DataRequired()],
                        render_kw={'placeholder': "URL de l'illustration finissant par une extension de fichier image "
                                                  "(comme sur l'exemple)"})
    submit = SubmitField('Ajouter')


class UsersSearchForm(FlaskForm):
    """
    Form to search users
    """
    username_hint = StringField('Nom de l\'utilisateur', id='search-input', render_kw={
        'class': 'form-control',
        'placeholder': 'Rechercher un utilisateur grâce à son nom',
        'aria-describedby': 'search-buttons'
    })
    display_favorites_players_only = BooleanField('Afficher uniquement les joueurs favoris')
    display_masked_players = BooleanField('Afficher les joueurs masqués')
    sort_order = SelectField('Ordre de tri : ', choices=[
        ('alphabetical', 'Alphabétique'),
        ('mostRecent', 'Plus récents en premier')
    ], render_kw={'class': 'custom-select inline-select'})
