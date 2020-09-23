from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from hgossipBack.config import DbEngine_config
from hgossipBack import create_db_engine, create_db_sessionFactory
from hgossipBack.models import User


class EditProfile(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    bio = TextAreaField('About me', validators=[Length(min=0, max=127)])
    submit = SubmitField('Submit')

    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.original_username = original_username


    def validate_username(self, username):
        from server import SQLSession
        session = SQLSession()
        conn = session.connection()
        if username.data != self.original_username:
            user = session.query(User).filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')