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

class SessionSearchForm(FlaskForm):
    sessions_hint = StringField("Nom d'une session", id='search-input', render_kw={
        'class': 'form-control',
        'placeholder': 'Rechercher des sessions en fonction du ...',
        'aria-describedby': 'search-buttons'
    })
    display_search_type = SelectField('Type', choices=[('title',"Nom d'un des jeux"),('date',"Date de la session")], render_kw={'class': 'inline-select'})
    display_search_parameter = RadioField('Catégorie de la recherche : ', choices=
        [(None, "Afficher toutes les sessions"),
            ('UPCOMING',"Afficher uniquement les sessions à venir"),
            ('PASSED',"Afficher uniquement les sessions terminées")
        ])
    sort_order = SelectField('Ordre de tri : ', choices=[
        ('mostRecent', 'Plus récents'),
        ('mostAncient', 'Plus vieux')
    ], render_kw={'class': 'custom-select inline-select'})
