from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class EditProfile(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    bio = TextAreaField('About me', validators=[Length(min=0, max=127)])
    submit = SubmitField('Submit')