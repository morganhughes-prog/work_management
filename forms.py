from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, URL


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=150)])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=150)])
    submit = SubmitField('Register')


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=2000)])
    work_class_id = SelectField('Task Class', coerce=str, validators=[Optional()])
    status = SelectField('Status', coerce=str, validators=[DataRequired()])
    lifecycle_stage = SelectField('Lifecycle Stage', coerce=str, validators=[DataRequired()])
    sprint_id = SelectField('Target Sprint', coerce=str, validators=[Optional()])
    attachment_url = StringField('Attach File URL', validators=[Optional(), URL(require_tld=False)])
    attachment_urls_json = HiddenField('Attachment URLs', validators=[Optional()])
    submit = SubmitField('Save Task')


class AdminClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(min=1, max=100)])
    parent_id = SelectField('Nest Under (Optional)', coerce=str, validators=[Optional()])
    submit = SubmitField('Create')
