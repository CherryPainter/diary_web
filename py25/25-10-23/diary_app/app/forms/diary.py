# diary_app/app/forms/diary.py
"""日记相关表单"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class DiaryForm(FlaskForm):
    """日记表单"""
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('内容', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField('保存')