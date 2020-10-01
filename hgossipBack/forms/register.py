from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from hgossipBack.models.usermodels import User

from hgossipBack.config import DbEngine_config
from hgossipBack import create_db_engine, create_db_sessionFactory

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
        engine = create_db_engine(DbEngine_config)
        SQLSession = create_db_sessionFactory(engine)
        session = SQLSession()
        conn = session.connection()
        user = session.query(User).filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))
        session.close()
        conn.close()

    
    def validate_email(self, email):
        engine = create_db_engine(DbEngine_config)
        SQLSession = create_db_sessionFactory(engine)
        session = SQLSession()
        conn = session.connection()
        user = session.query(User).filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Email address already exists.'))
        session.close()
        conn.close()
