# diary_app/app/routes/auth_routes.py
"""认证相关路由"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegisterForm, LoginForm
from app.services import auth_service, system_service
from app.extensions import limiter

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.before_request
def check_maintenance_mode():
    """检查系统维护模式"""
    if system_service.is_maintenance_mode() and not request.endpoint == 'auth.login':
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    # 检查是否允许注册
    if not system_service.is_registration_open():
        flash('当前不允许新用户注册', 'warning')
        return redirect(url_for('auth.login'))
    
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('diary.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # 调用服务层进行注册
        success, user, message = auth_service.register_user(
            form.username.data,
            form.email.data,
            form.password.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute', error_message='登录尝试次数过多，请稍后再试')
def login():
    """用户登录"""
    # 如果已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('diary.index'))
    
    # 检查维护模式
    if system_service.is_maintenance_mode():
        flash('系统正在维护中，请稍后再试', 'warning')
    
    form = LoginForm()
    # 处理解锁请求
    if request.method == 'POST' and 'unlock' in request.form:
        # 处理账户解锁
        if request.form.get('unlock') == 'true':
            username = request.form.get('username')
            answer = request.form.get('security_answer')
            
            success, message = auth_service.verify_security_answer(username, answer)
            if success:
                flash(message, 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(message, 'danger')
                session['locked_username'] = username
                return redirect(url_for('auth.login'))
    
    # 处理登录请求
    elif form.validate_on_submit():
        # 调用服务层进行登录
        success, user, is_locked, question, message = auth_service.login_user(
            form.username.data,
            form.password.data,
            request.remote_addr
        )
        
        if success:
            # 登录成功
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('diary.index'))
        elif is_locked:
            # 账户锁定，显示安全问题
            flash(message, 'danger')
            session['locked_username'] = form.username.data
            session['security_question'] = question
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    # 检查是否需要显示解锁表单
    locked_username = session.pop('locked_username', None)
    security_question = session.pop('security_question', None)
    
    return render_template(
        'login.html', 
        form=form,
        locked_username=locked_username,
        security_question=security_question
    )

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/verify')
@login_required
def verify():
    """账户验证"""
    # 这里可以实现额外的验证逻辑，如邮箱验证、双因素认证等
    flash('账户验证功能尚未实现', 'info')
    return redirect(url_for('diary.index'))