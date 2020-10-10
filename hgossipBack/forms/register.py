from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from hgossipBack.models.usermodels import User


from flask_babel import _, lazy_gettext as _l


class RegistrationForm(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField(_l('Register'))


    def validate_username(self, username):
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        user = session.query(User).filter_by(username=username.data).first()
        session.close()
        connection.close()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))


    
    def validate_email(self, email):
        from server import SQLSession
        session = SQLSession()
        connection = session.connection()
        user = session.query(User).filter_by(email=email.data).first()
        session.close()
        connection.close()
        if user is not None:
            raise ValidationError(_l('Email address already exists.'))
