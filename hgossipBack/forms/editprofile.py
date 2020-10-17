from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from hgossipBack.models import User

from flask_babel import _, lazy_gettext as _l


class EditProfile(FlaskForm):
    username = StringField(_l('username'), validators=[DataRequired()])
    bio = TextAreaField(_l('About me'), validators=[Length(min=0, max=127)])
    submit = SubmitField(_l('Submit'))

    
    def __init__(self, original_username, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.original_username = original_username


    def validate_username(self, username):
        if username.data != self.original_username:
            from server import SQLSession
            session = SQLSession()
            connection = session.connection()
            user = session.query(User).filter_by(username=self.username.data).first()
            session.close()
            connection.close()
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))