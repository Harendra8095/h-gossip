from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from hgossipBack.models.usermodels import User


from flask_babel import _, lazy_gettext as _l

from server import SQLSession

class RegistrationForm(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField(_l('Register'))


    def validate_username(self, username):
        session = SQLSession()
        user = session.query(User).filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))


    
    def validate_email(self, email):
        session = SQLSession()
        user = session.query(User).filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Email address already exists.'))
