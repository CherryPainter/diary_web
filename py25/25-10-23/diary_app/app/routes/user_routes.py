"""用户路由模块 - 处理用户相关的HTTP请求"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp
import tempfile
from app.services.user_service import user_service
from app.utils.data import generate_export_file

# 创建用户路由蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')

# 认证相关表单
class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名/邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(), 
        Length(min=3, max=50),
        Regexp(r'^[a-zA-Z0-9_]+$', message='用户名只能包含字母、数字和下划线')
    ])
    email = EmailField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(), 
        Length(min=8, max=128)
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(), 
        EqualTo('password', message='两次输入密码不一致')
    ])
    submit = SubmitField('注册')

# 用户资料表单
class ProfileForm(FlaskForm):
    """用户资料表单"""
    username = StringField('用户名', validators=[
        DataRequired(), 
        Length(min=3, max=50),
        Regexp(r'^[a-zA-Z0-9_]+$', message='用户名只能包含字母、数字和下划线')
    ])
    email = EmailField('邮箱', validators=[DataRequired(), Email()])
    full_name = StringField('真实姓名', validators=[Length(max=100)])
    bio = TextAreaField('个人简介', validators=[Length(max=500)])
    avatar_url = StringField('头像URL', validators=[Length(max=255)])
    submit = SubmitField('保存')

class PasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('new_password', message='两次输入密码不一致')])
    submit = SubmitField('修改密码')

class SecuritySettingsForm(FlaskForm):
    """安全设置表单"""
    question = StringField('安全问题', validators=[DataRequired(), Length(max=255)])
    answer = PasswordField('安全问题答案', validators=[DataRequired()])
    submit = SubmitField('保存设置')

class DeleteAccountForm(FlaskForm):
    """删除账户表单"""
    confirm_password = PasswordField('确认密码', validators=[DataRequired()])
    confirm_deletion = BooleanField('我确认要删除我的账户', validators=[DataRequired()])
    submit = SubmitField('删除账户')

# 认证相关路由
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # 创建新用户
            user = user_service.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            
            # 登录新用户
            login_user(user)
            flash('注册成功！欢迎来到日记应用', 'success')
            return redirect(url_for('main.index'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('注册失败，请稍后重试', 'error')
    
    return render_template('user/register.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # 认证用户
        user, error_msg = user_service.authenticate_user(
            username=form.username.data,
            password=form.password.data
        )
        
        if user:
            # 登录用户
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('登录成功！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash(error_msg, 'error')
    
    return render_template('user/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('main.index'))

# 用户资料路由
@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户个人资料"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            # 更新用户资料
            user_service.update_user_profile(
                user_id=current_user.id,
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data,
                bio=form.bio.data,
                avatar_url=form.avatar_url.data
            )
            flash('个人资料已更新', 'success')
            return redirect(url_for('user.profile'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('更新失败，请稍后重试', 'error')
    
    return render_template('user/profile.html', form=form)

@user_bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password_old():
    """修改密码（旧路径）"""
    form = PasswordForm()
    
    if form.validate_on_submit():
        # 修改密码
        success, message = user_service.update_password(
            user=current_user,
            old_password=form.old_password.data,
            new_password=form.new_password.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.profile'))
        else:
            flash(message, 'error')
    
    return render_template('user/password.html', form=form)

# 用户统计路由
@user_bp.route('/stats')
@login_required
def user_stats():
    """用户统计信息"""
    try:
        stats = user_service.get_user_stats(current_user.id)
        return render_template('user/stats.html', stats=stats)
    except Exception as e:
        flash('获取统计信息失败', 'error')
        return redirect(url_for('user.profile'))

# 账户管理路由
@user_bp.route('/settings')
@login_required
def settings():
    """用户设置页面"""
    # 获取用户的安全问题
    security_question = None
    if current_user.security_profile and current_user.security_profile.question:
        security_question = current_user.security_profile.question
    
    return render_template(
        'settings.html', 
        security_question=security_question,
        security_levels={1: '低', 2: '中', 3: '高'}
    )

@user_bp.route('/settings/password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = PasswordForm()
    
    if form.validate_on_submit():
        # 调用服务层修改密码
        success, message = user_service.update_password(
            current_user,
            form.old_password.data,
            form.new_password.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.settings'))
        else:
            flash(message, 'danger')
    
    return render_template('change_password.html', form=form)

@user_bp.route('/settings/security', methods=['GET', 'POST'])
@login_required
def security_settings():
    """安全设置"""
    form = SecuritySettingsForm()
    
    # 如果已设置安全问题，预填充
    if current_user.security_profile and current_user.security_profile.question:
        form.question.data = current_user.security_profile.question
    
    if form.validate_on_submit():
        # 调用服务层更新安全设置
        success, message = user_service.update_security_settings(
            current_user,
            form.question.data,
            form.answer.data
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('user.settings'))
        else:
            flash(message, 'danger')
    
    return render_template('security_settings.html', form=form)

@user_bp.route('/settings/security-level', methods=['POST'])
@login_required
def update_security_level():
    """更新安全等级"""
    level = request.form.get('security_level', type=int)
    
    if level not in [1, 2, 3]:
        flash('无效的安全等级', 'danger')
        return redirect(url_for('user.settings'))
    
    # 调用服务层更新安全等级
    success, message = user_service.update_security_level(current_user, level)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user.settings'))

@user_bp.route('/export-data')
@login_required
def export_data():
    """导出用户数据"""
    try:
        # 生成导出文件
        file_content, filename, content_type = generate_export_file(current_user)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
            temp.write(file_content)
            temp_path = temp.name
        
        # 发送文件
        return send_file(
            temp_path, 
            as_attachment=True, 
            download_name=filename, 
            mimetype=content_type
        )
    except Exception as e:
        flash(f'数据导出失败: {str(e)}', 'danger')
        return redirect(url_for('user.settings'))

@user_bp.route('/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """停用账户（需要二次确认）"""
    try:
        # 这里可以添加额外的安全验证，例如要求重新输入密码
        user_service.deactivate_user(current_user.id)
        logout_user()
        flash('账户已成功停用', 'info')
        return redirect(url_for('main.index'))
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('操作失败，请稍后重试', 'error')
    
    return redirect(url_for('user.profile'))

@user_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """删除账户"""
    form = DeleteAccountForm()
    
    if form.validate_on_submit():
        # 调用服务层删除账户
        success, message = user_service.delete_user_account(
            current_user,
            form.confirm_password.data
        )
        
        if success:
            # 退出登录并重定向到登录页面
            flash(message, 'success')
            logout_user()
            return redirect(url_for('user.login'))
        else:
            flash(message, 'danger')
    
    return render_template('user/delete_account.html', form=form)

# 管理员路由
@user_bp.route('/admin/users')
@login_required
def admin_users():
    """管理员查看所有用户（需要管理员权限）"""
    if not current_user.is_admin:
        flash('无权访问此页面', 'error')
        return redirect(url_for('main.index'))
    
    # 获取用户列表，支持分页和筛选
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    # 使用服务层获取用户列表
    pagination = user_service.get_user_list(
        page=page,
        per_page=20,
        search=search
    )
    
    return render_template('user/admin/users.html', pagination=pagination, search=search)

@user_bp.route('/admin/user/<int:user_id>/reset')
@login_required
def admin_reset_password(user_id):
    """管理员重置用户密码"""
    if not current_user.is_admin:
        flash('无权执行此操作', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 生成一个临时密码
        import random
        import string
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # 重置密码
        user_service.reset_password(user_id, temp_password)
        
        # 在实际应用中，应该通过邮件发送临时密码
        flash(f'用户密码已重置为临时密码：{temp_password}，请妥善保存', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('重置密码失败', 'error')
    
    return redirect(url_for('user.admin_users'))

@user_bp.route('/admin/user/<int:user_id>/toggle')
@login_required
def admin_toggle_user(user_id):
    """管理员激活/停用用户"""
    if not current_user.is_admin:
        flash('无权执行此操作', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # 获取用户信息
        user = user_service.get_user_by_id(user_id)
        if user:
            # 切换用户状态
            if user.is_active:
                user_service.deactivate_user(user_id)
                flash('用户已停用', 'success')
            else:
                user_service.activate_user(user_id)
                flash('用户已激活', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('操作失败', 'error')
    
    return redirect(url_for('user.admin_users'))

@user_bp.route('/profile/simple')
@login_required
def profile_simple():
    """用户个人资料简单页面（备用）"""
    return render_template('profile.html')