# diary_app/app/routes/admin_routes.py
"""管理员相关路由"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.forms import AdminUserForm, SystemStatusForm
from app.services import admin_service, system_service

# 创建蓝图
admin_bp = Blueprint('admin', __name__)

from functools import wraps

# 管理员权限检查装饰器
def admin_required(func):
    """检查是否为管理员"""
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash('没有管理员权限', 'danger')
            return redirect(url_for('diary.index'))
        return func(*args, **kwargs)
    return decorated_view

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """管理员面板"""
    # 获取系统统计信息
    stats = system_service.get_system_statistics()
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@admin_required
def users():
    """用户管理页面"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 获取用户列表
    pagination = admin_service.get_all_users(page, per_page)
    
    return render_template('admin/users.html', pagination=pagination)

@admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = admin_service.get_user_by_id(user_id)
    
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('admin.users'))
    
    form = AdminUserForm(obj=user)
    
    if form.validate_on_submit():
        # 更新用户信息
        user.username = form.username.data
        user.email = form.email.data
        
        # 特殊处理管理员权限和安全等级
        if form.is_admin.data != user.is_admin:
            success, message = admin_service.update_user_role(user_id, form.is_admin.data)
            if not success:
                flash(message, 'danger')
                return render_template('admin/edit_user.html', form=form, user=user)
        
        if form.security_level.data != user.security_level:
            success, message = admin_service.update_user_security_level(user_id, form.security_level.data)
            if not success:
                flash(message, 'danger')
                return render_template('admin/edit_user.html', form=form, user=user)
        
        from app.extensions import db
        try:
            db.session.commit()
            flash('用户信息已更新', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(user_id):
    """重置用户密码"""
    new_password = request.form.get('new_password')
    
    if not new_password:
        flash('请输入新密码', 'danger')
        return redirect(url_for('admin.edit_user', user_id=user_id))
    
    # 调用服务层重置密码
    success, message = admin_service.reset_user_password(user_id, new_password)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.edit_user', user_id=user_id))

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    # 调用服务层删除用户
    success, message = admin_service.delete_user(user_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/system-settings', methods=['GET', 'POST'])
@admin_required
def system_settings():
    """系统设置页面"""
    # 获取当前系统设置
    current_settings = system_service.get_system_status()
    
    # 初始化表单
    form = SystemStatusForm(
        maintenance_mode=current_settings.get('maintenance_mode') == 'true',
        login_attempts_limit=int(current_settings.get('max_login_attempts', 5)),
        session_timeout=int(current_settings.get('session_timeout', 3600)) // 60  # 转换为分钟
    )
    
    if form.validate_on_submit():
        # 准备设置数据
        settings = {
            'maintenance_mode': 'true' if form.maintenance_mode.data else 'false',
            'max_login_attempts': str(form.login_attempts_limit.data),
            'session_timeout': str(form.session_timeout.data * 60),  # 转换为秒
            'registration_open': request.form.get('registration_open', 'false')
        }
        
        # 调用服务层更新系统设置
        success, message = admin_service.update_system_settings(settings, current_user.id)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.system_settings'))
        else:
            flash(message, 'danger')
    
    return render_template(
        'admin/system_settings.html', 
        form=form,
        current_settings=current_settings
    )

@admin_bp.route('/logs')
@admin_required
def logs():
    """系统日志页面"""
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    log_type = request.args.get('type', None)
    
    # 获取日志
    from app.utils.logging import get_system_logs
    pagination = get_system_logs(log_type, page, per_page)
    
    return render_template('admin/logs.html', pagination=pagination, log_type=log_type)

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
@login_required
def create_admin():
    """创建管理员（仅现有管理员可用）"""
    if not current_user.is_admin:
        flash('没有管理员权限', 'danger')
        return redirect(url_for('diary.index'))
    
    from flask_wtf import FlaskForm
    from wtforms import StringField, PasswordField, EmailField, SubmitField
    from wtforms.validators import DataRequired, Email, Length
    
    class CreateAdminForm(FlaskForm):
        username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=50)])
        email = EmailField('邮箱', validators=[DataRequired(), Email()])
        password = PasswordField('密码', validators=[DataRequired(), Length(min=8)])
        submit = SubmitField('创建管理员')
    
    form = CreateAdminForm()
    
    if form.validate_on_submit():
        # 调用服务层创建管理员
        success, user, message = admin_service.create_admin_user(
            form.username.data,
            form.email.data,
            form.password.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.users'))
        else:
            flash(message, 'danger')
    
    return render_template('admin/create_admin.html', form=form)