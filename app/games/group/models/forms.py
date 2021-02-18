from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class JoinPrivateGroupForm(FlaskForm):
    """
    Form for users to join a private group with a code
    """
    code = StringField('Code', validators=[DataRequired()], render_kw={'placeholder': 'Code'})
    submit = SubmitField('Rejoindre')
