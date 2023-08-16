from wtforms import Form, StringField, PasswordField, validators, IntegerField, TextAreaField, DateField, TimeField, EmailField, ValidationError, BooleanField, HiddenField, SelectField
from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegisterForm(FlaskForm):
    username = StringField("Username", [
        validators.Length(min=2, max=20),
        validators.Regexp(
                r'^[A-Za-z][A-Za-z0-9_.]*$',
                0,
                "Usernames must have only letters, " "numbers, dots or underscores",
            )
        ])
    email = EmailField("Email", [validators.DataRequired()])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.Length(min=8),
        validators.EqualTo("confirm", message="Passwords must match")
    ])
    confirm = PasswordField("Confirm Password")

class LoginForm(FlaskForm):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password",[
        validators.DataRequired()
    ])

class CollectionForm(FlaskForm):
    collection_name = StringField("Title", [validators.DataRequired()])
    collection_desc = TextAreaField("Description (Optional)")
    collection_boolean = BooleanField("Public?")

class GameForm(FlaskForm): # Simple form for searching things (will not use async)
    game_title = StringField("Title")

class FragForm(FlaskForm): # For manual input
    date_started = DateField("Date", [validators.DataRequired()])
    time_started = TimeField("Time", [validators.DataRequired()], format="%H:%M")
    time_played = IntegerField("Playtime", [validators.DataRequired()])
    unit = SelectField(validators=[validators.DataRequired()], choices=["Hours", "Minutes", "Seconds"])

class RatingForm(FlaskForm):
    review = TextAreaField()