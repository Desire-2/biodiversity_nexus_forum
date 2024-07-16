from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio')
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in use. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('Upload File', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'docx'])])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
  


class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"id": "editor"})
    file = FileField('Upload File', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'docx'])])
    submit = SubmitField('Upload Article')

class ForumForm(FlaskForm):
    name = StringField('Forum Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()], render_kw={"class": "tinymce"})
    file = FileField('Upload File', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'docx'])])
    submit = SubmitField('Create Forum')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"class": "tinymce"})
    file = FileField('Upload File', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'docx'])])
    creator = StringField('Creator', validators=[DataRequired()])
    submit = SubmitField('Create Blog')
    

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class MessageForm(FlaskForm):
    recipient = StringField('Recipient', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

