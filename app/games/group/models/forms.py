from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired

class JoinPrivateGroupForm(FlaskForm):
    """
    Form for users to join a private group with a code
    """
    code = StringField('Code', validators=[DataRequired()], render_kw={'placeholder': 'Code'})
    submit = SubmitField('Rejoindre')


class AddGroupForm(FlaskForm):
    """
    Form to create a new public or private group
    """
    name = StringField('Nom', validators=[DataRequired()], render_kw={'placeholder': 'Nom'})
    is_private = RadioField('Visibilité', validators=[DataRequired()], choices=[
        ('private',"Privé (on ne peut rejoindre votre groupe qu'avec un mot de passe)"),
        ('public',"Public (tout le monde peut rejoindre votre groupe)")])
    password = StringField('Mot de passe', render_kw={'placeholder': 'Mot de passe'})
    submit = SubmitField('Créer')
