# diary_app/app/forms/admin.py
"""管理员相关表单"""
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class AdminUserForm(FlaskForm):
    """管理员编辑用户表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(max=120)])
    is_admin = BooleanField('管理员权限')
    security_level = SelectField('安全等级', coerce=int, choices=[(1, '低'), (2, '中'), (3, '高')])
    submit = SubmitField('保存')

class SystemStatusForm(FlaskForm):
    """系统状态配置表单"""
    maintenance_mode = BooleanField('维护模式')
    login_attempts_limit = IntegerField('登录尝试限制', validators=[DataRequired()])
    account_lockout_duration = IntegerField('账户锁定时长（分钟）', validators=[DataRequired()])
    default_security_level = SelectField('默认安全等级', coerce=int, choices=[(1, '低'), (2, '中'), (3, '高')])
    session_timeout = IntegerField('会话超时时间（分钟）', validators=[DataRequired()])
    require_two_factor = BooleanField('要求双因素认证')
    version = StringField('系统版本', validators=[DataRequired()])
    maintenance_message = TextAreaField('维护消息')
    submit = SubmitField('保存配置')