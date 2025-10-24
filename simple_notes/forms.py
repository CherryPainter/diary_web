from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='两次输入密码不一致')])
    submit = SubmitField('注册')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class NoteForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('内容', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField('保存')