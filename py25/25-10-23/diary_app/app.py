"""Flask 日记应用主入口文件"""
import os
import mimetypes
import secrets
from dotenv import load_dotenv
from flask import request
from app.utils.logging import log_system_event
from app.models import SystemLog

# 设置 MIME 类型
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

# 加载环境变量
load_dotenv()

# 导入应用工厂函数
from app import create_app

# 创建应用实例
app = create_app()

# 开发环境下的运行配置
if __name__ == '__main__':
    # 从环境变量获取端口，默认使用 5000
    port = int(os.environ.get('PORT', 5000))
    # 启用调试模式以便查看详细错误信息
    debug = True
    
    # 启动应用
    app.run(host='0.0.0.0', port=port, debug=debug)

# 辅助函数：验证安全令牌
def verify_security_token(user_id, token):
    # 简单实现，实际应从Redis或数据库中获取并验证
    # 在生产环境中应实现带过期时间的令牌验证
    return token is not None

# 辅助函数：获取用户活动记录
def get_user_activity_logs(user_id, limit=50):
    return SystemLog.query.filter_by(user_id=user_id).order_by(SystemLog.created_at.desc()).limit(limit).all()

# 辅助函数：生成恢复码
def generate_recovery_codes():
    # 生成10个恢复码
    codes = [secrets.token_hex(4).upper() for _ in range(10)]
    return codes

# 辅助函数：发送验证邮件（模拟）
def send_verification_email(email, subject, message):
    # 实际应用中应使用真正的邮件发送服务
    log_system_event('info', f'模拟发送邮件到 {email}，主题：{subject}', None, request.remote_addr)
    return True

# 安全响应头（基础版）
@app.after_request
def set_security_headers(response):
    # 最小化的 CSP；允许本站与 jsDelivr，并支持内联脚本 nonce
    nonce = getattr(g, 'csp_nonce', None)
    csp = [
        "default-src 'self'",
        f"script-src 'self' https://cdn.jsdelivr.net" + (f" 'nonce-{nonce}'" if nonce else ""),
        "style-src 'self' https://cdn.jsdelivr.net",
        "font-src 'self' https://cdn.jsdelivr.net",
        "img-src 'self' data:"
    ]
    response.headers['Content-Security-Policy'] = '; '.join(csp)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'

    # 修正静态资源的 Content-Type（避免 .js 被标记为 text/plain）
    try:
        p = request.path
        if p.startswith('/static/'):
            if p.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
            elif p.endswith('.css'):
                response.headers['Content-Type'] = 'text/css; charset=utf-8'
    except Exception:
        pass

    return response

@app.before_request
def set_csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(16)

# 全局安全检查
@app.before_request
def global_security_check():
    # 检查系统维护状态
    if request.endpoint not in ['login', 'logout'] and current_user.is_authenticated:
        maintenance_mode = SystemStatus.query.filter_by(status_key='maintenance_mode').first()
        if maintenance_mode and maintenance_mode.status_value == 'true' and not current_user.is_admin:
            flash('系统正在维护中，请稍后再试', 'warning')
            return redirect(url_for('logout'))

# 路由
@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('index.html', pagination=pagination, entries=pagination.items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        # 唯一性检查
        if User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first():
            flash('用户名或邮箱已存在', 'danger')
            return render_template('register.html', form=form)
        user = User(username=form.username.data.strip(), email=form.email.data.strip())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
    flash('注册成功，请登录', 'success')
    return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit(lambda: login_rate_limit)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    username_param = request.args.get('u')
    locked_user = None
    security_question = None
    if username_param:
        u = User.query.filter_by(username=username_param.strip()).first()
        if u and u.security_profile and (u.security_profile.locked_until and u.security_profile.locked_until > datetime.utcnow() or u.security_profile.failed_count >= 3):
            locked_user = u.username
            security_question = u.security_profile.question

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        # 用户不存在或密码不匹配
        if not user or (user.security_profile and (user.security_profile.locked_until and user.security_profile.locked_until > datetime.utcnow() or user.security_profile.failed_count >= 3)):
            if user and user.security_profile and user.security_profile.failed_count >= 3:
                flash('账户已锁定，请使用辅助验证解锁。', 'warning')
                return render_template('login.html', form=form, locked_user=user.username, security_question=user.security_profile.question)
            flash('用户名或密码错误', 'danger')
            return render_template('login.html', form=form, locked_user=locked_user, security_question=security_question)

        if not user.check_password(form.password.data):
            # 记录失败次数
            profile = user.security_profile
            if not profile:
                profile = SecurityProfile(user_id=user.id, failed_count=0)
                db.session.add(profile)
            profile.failed_count = (profile.failed_count or 0) + 1
            if profile.failed_count >= 3:
                profile.locked_until = None  # 设置为无限期锁定，需辅助验证解锁
                flash('账户已锁定，请使用辅助验证解锁。', 'warning')
                db.session.commit()
                return render_template('login.html', form=form, locked_user=user.username, security_question=profile.question)
            db.session.commit()
            flash('用户名或密码错误', 'danger')
            return render_template('login.html', form=form)

        # 密码正确
        if user.security_profile and (user.security_profile.locked_until and user.security_profile.locked_until > datetime.utcnow() or user.security_profile.failed_count >= 3):
            flash('账户处于锁定状态，请先通过辅助验证解锁。', 'warning')
            return render_template('login.html', form=form, locked_user=user.username, security_question=user.security_profile.question)

        # 清理失败记录
        if user.security_profile:
            user.security_profile.failed_count = 0
            user.security_profile.locked_until = None
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        
        login_user(user)
        db.session.commit()
        
        # 记录登录事件
        log_system_event('info', f'用户 {user.username} 登录成功', user.id, request.remote_addr)
        flash('登录成功', 'success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('main.index'))
    return render_template('login.html', form=form, locked_user=locked_user, security_question=security_question)

@app.route('/logout')
@login_required
def logout():
    # 记录登出事件
    log_system_event('info', f'用户 {current_user.username} 退出登录', current_user.id, request.remote_addr)
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('auth.login'))

@app.route('/entry/new', methods=['GET', 'POST'])
@login_required
def create_entry():
    form = DiaryForm()
    if form.validate_on_submit():
        entry = DiaryEntry(user_id=current_user.id, title=form.title.data.strip(), content=form.content.data)
        db.session.add(entry)
        db.session.commit()
        flash('日记已创建', 'success')
        return redirect(url_for('main.index'))
    return render_template('entry_form.html', form=form, mode='create')

@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        abort(404)
    form = DiaryForm(obj=entry)
    if form.validate_on_submit():
        entry.title = form.title.data.strip()
        entry.content = form.content.data
        db.session.commit()
        flash('日记已更新', 'success')
        return redirect(url_for('main.index'))
    return render_template('entry_form.html', form=form, mode='edit')

@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    # 检查安全要求
    if not check_security_requirements(current_user, 'delete_entry'):
        # 对于高安全级别用户，需要额外验证
        if current_user.security_level == 3:
            token = generate_security_token(current_user.id)
            response = redirect(url_for('verify_security', token=token, next=request.url))
            response.set_cookie('security_token_temp', token, httponly=True, secure=app.config['SESSION_COOKIE_SECURE'])
            return response
    
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        abort(404)
    
    db.session.delete(entry)
    db.session.commit()
    
    # 记录删除操作
    log_system_event('warning', f'用户 {current_user.username} 删除了日记条目 {entry_id}', current_user.id, request.remote_addr)
    flash('日记已删除', 'info')
    return redirect(url_for('main.index'))

@app.route('/login/aux-verify', methods=['POST'])
def aux_verify():
    username = request.form.get('username', '').strip()
    answer = request.form.get('answer', '')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('auth.login'))
    profile = user.security_profile
    if not profile or not profile.question or not profile.answer_hash:
        flash('未设置辅助验证，无法解锁。', 'danger')
        return redirect(url_for('auth.login', u=username))
    if not check_password_hash(profile.answer_hash, answer):
        flash('辅助验证答案错误。', 'danger')
        return redirect(url_for('auth.login', u=username))
    # 验证通过，解除锁定
    profile.failed_count = 0
    profile.locked_until = None
    db.session.commit()
    flash('账户已解锁，请重新登录。', 'success')
    return redirect(url_for('auth.login', u=username))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile = current_user.security_profile
    if not profile:
        profile = SecurityProfile(user_id=current_user.id, failed_count=0)
        db.session.add(profile)
        db.session.commit()
    
    # 获取用户活动记录
    activity_logs = get_user_activity_logs(current_user.id)
    
    # 获取日记统计信息
    total_entries = DiaryEntry.query.filter_by(user_id=current_user.id).count()
    recent_entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.created_at.desc()).limit(5).all()

    if request.method == 'POST':
        form_name = request.form.get('form')
        
        # 密码修改表单处理
        if form_name == 'password':
            # 检查安全要求
            if not check_security_requirements(current_user, 'change_password'):
                if current_user.security_level == 3:
                    token = generate_security_token(current_user.id)
                    response = redirect(url_for('verify_security', token=token, next=request.url))
                    response.set_cookie('security_token_temp', token, httponly=True, secure=app.config['SESSION_COOKIE_SECURE'])
                    return response
            
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new = request.form.get('confirm_new', '')
            
            # 根据安全等级增加密码复杂性要求
            if current_user.security_level >= 2:
                if not (any(c.isupper() for c in new_password) and any(c.islower() for c in new_password) and any(c.isdigit() for c in new_password)):
                    flash('密码必须包含大小写字母和数字', 'danger')
                    return render_template('settings.html', profile=profile, activity_logs=activity_logs, total_entries=total_entries, recent_entries=recent_entries)
            
            if not current_user.check_password(old_password):
                flash('旧密码错误', 'danger')
            elif not new_password or len(new_password) < 8:
                flash('新密码长度至少8位', 'danger')
            elif new_password != confirm_new:
                flash('两次输入的新密码不一致', 'danger')
            else:
                # 检查是否与历史密码重复
                if profile.password_history:
                    from ast import literal_eval
                    try:
                        password_history = literal_eval(profile.password_history)
                        if any(check_password_hash(hash_val, new_password) for hash_val in password_history):
                            flash('新密码不能与最近使用的密码相同', 'danger')
                            return render_template('settings.html', profile=profile, activity_logs=activity_logs, total_entries=total_entries, recent_entries=recent_entries)
                    except:
                        pass
                
                # 更新密码
                current_user.set_password(new_password)
                
                # 更新安全信息
                profile.last_password_change = datetime.utcnow()
                
                # 保存密码历史（最近3个）
                if profile.password_history:
                    try:
                        password_history = literal_eval(profile.password_history)
                        password_history = [current_user.password_hash] + password_history[:2]  # 保留最近3个
                        profile.password_history = str(password_history)
                    except:
                        profile.password_history = str([current_user.password_hash])
                else:
                    profile.password_history = str([current_user.password_hash])
                
                db.session.commit()
                log_system_event('security', f'用户 {current_user.username} 修改了密码', current_user.id, request.remote_addr)
                flash('密码已更新', 'success')
                return redirect(url_for('settings') + '#password')
        
        # 安全问题设置表单处理
        elif form_name == 'security':
            question = request.form.get('question', '').strip()
            answer = request.form.get('answer', '')
            two_factor_enabled = 'two_factor_enabled' in request.form
            
            if not question or not answer:
                flash('请填写问题和答案', 'danger')
            else:
                profile.question = question
                profile.answer_hash = generate_password_hash(answer)
                profile.two_factor_enabled = two_factor_enabled
                db.session.commit()
                log_system_event('security', f'用户 {current_user.username} 更新了安全设置', current_user.id, request.remote_addr)
                flash('辅助验证已保存', 'success')
                return redirect(url_for('settings') + '#security')
        
        # 安全等级设置表单处理
        elif form_name == 'security_level':
            security_level = request.form.get('security_level', type=int)
            if security_level and security_level in [1, 2, 3]:
                current_user.security_level = security_level
                db.session.commit()
                log_system_event('info', f'用户 {current_user.username} 修改了安全等级为 {security_level}', current_user.id, request.remote_addr)
                flash('安全等级已更新', 'success')
                return redirect(url_for('settings') + '#security_level')
        
        # 数据管理操作处理
        elif form_name == 'data_management':
            action = request.form.get('action')
            
            # 导出数据操作
            if action == 'export':
                # 创建一个导出文件
                import json
                export_data = {
                    'user_info': {
                        'username': current_user.username,
                        'email': current_user.email,
                        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
                        'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                        'security_level': current_user.security_level
                    },
                    'diary_entries': []
                }
                
                # 添加所有日记条目
                entries = DiaryEntry.query.filter_by(user_id=current_user.id).all()
                for entry in entries:
                    export_data['diary_entries'].append({
                        'id': entry.id,
                        'title': entry.title,
                        'content': entry.content,
                        'created_at': entry.created_at.isoformat(),
                        'updated_at': entry.updated_at.isoformat()
                    })
                
                # 生成JSON响应
                log_system_event('info', f'用户 {current_user.username} 导出了个人数据', current_user.id, request.remote_addr)
                return json.dumps(export_data, ensure_ascii=False, indent=2), 200, {'Content-Type': 'application/json', 'Content-Disposition': f'attachment; filename=diary_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'}
            
            # 删除账户操作（需要二次确认）
            elif action == 'delete_account':
                confirm_deletion = request.form.get('confirm_deletion')
                confirm_password = request.form.get('confirm_password')
                
                if confirm_deletion != 'DELETE' or not current_user.check_password(confirm_password):
                    flash('删除确认不正确或密码错误', 'danger')
                else:
                    # 记录删除账户事件
                    log_system_event('warning', f'用户 {current_user.username} 删除了自己的账户', current_user.id, request.remote_addr)
                    
                    # 登出用户
                    username = current_user.username
                    user_id = current_user.id
                    logout_user()
                    
                    # 删除用户（级联删除关联数据）
                    user = User.query.get(user_id)
                    if user:
                        db.session.delete(user)
                        db.session.commit()
                    
                    flash('您的账户已成功删除', 'success')
                    return redirect(url_for('auth.login'))
    
    # 传递所有必要的数据到模板
    return render_template(
        'settings.html', 
        profile=profile, 
        activity_logs=activity_logs,
        total_entries=total_entries,
        recent_entries=recent_entries
    )

# 错误页
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# 安全验证页面
@app.route('/verify-security', methods=['GET', 'POST'])
@login_required
def verify_security():
    token = request.args.get('token')
    next_url = request.args.get('next', url_for('main.index'))
    
    if not token:
        flash('无效的安全验证请求', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # 验证用户回答
        answer = request.form.get('answer', '')
        profile = current_user.security_profile
        
        if profile and profile.question and profile.answer_hash:
            if check_password_hash(profile.answer_hash, answer):
                # 验证通过，设置安全令牌
                security_token = generate_security_token(current_user.id)
                response = redirect(next_url)
                response.set_cookie('security_token', security_token, httponly=True, secure=app.config['SESSION_COOKIE_SECURE'])
                log_system_event('security', f'用户 {current_user.username} 通过了安全验证', current_user.id, request.remote_addr)
                return response
            else:
                flash('验证失败，请重试', 'danger')
        else:
            flash('未设置辅助验证，请先在设置中配置', 'warning')
            return redirect(url_for('settings'))
    
    return render_template('verify_security.html', token=token, next_url=next_url)

# 管理员后台路由
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    # 获取系统状态
    system_status = SystemStatus.query.all()
    status_dict = {s.status_key: s.status_value for s in system_status}
    
    # 获取用户统计
    total_users = User.query.count()
    active_users = User.query.filter(User.last_login > datetime.utcnow() - timedelta(days=30)).count()
    
    # 获取最近的系统日志
    recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(20).all()
    
    # 获取日记统计
    total_entries = DiaryEntry.query.count()
    recent_entries = DiaryEntry.query.order_by(DiaryEntry.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                           status_dict=status_dict,
                           total_users=total_users,
                           active_users=active_users,
                           recent_logs=recent_logs,
                           total_entries=total_entries,
                           recent_entries=recent_entries)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    if user.is_admin and user.id != current_user.id:
        flash('不能编辑其他管理员账户', 'danger')
        return redirect(url_for('admin_users'))
    
    form = AdminUserForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        log_system_event('admin', f'管理员 {current_user.username} 编辑了用户 {user.username}', current_user.id, request.remote_addr)
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/system-status', methods=['GET', 'POST'])
@login_required
def admin_system_status():
    if not current_user.is_admin:
        abort(403)
    
    # 获取或创建系统配置
    status_keys = {
        'maintenance_mode': 'false',
        'login_attempts_limit': '5',
        'account_lockout_duration': '30',
        'default_security_level': '1',
        'session_timeout': '60',
        'require_two_factor': 'false',
        'version': '1.0.0',
        'maintenance_message': '系统正在维护，请稍后再试。'
    }
    
    # 确保所有状态键都存在
    for key, default_value in status_keys.items():
        status = SystemStatus.query.filter_by(status_key=key).first()
        if not status:
            status = SystemStatus(status_key=key, status_value=default_value)
            db.session.add(status)
    db.session.commit()
    
    # 构建状态字典
    status_dict = {}
    for status in SystemStatus.query.all():
        status_dict[status.status_key] = status.status_value
    
    # 准备表单数据
    form = SystemStatusForm(
        maintenance_mode=status_dict.get('maintenance_mode') == 'true',
        login_attempts_limit=int(status_dict.get('login_attempts_limit', '5')),
        account_lockout_duration=int(status_dict.get('account_lockout_duration', '30')),
        default_security_level=int(status_dict.get('default_security_level', '1')),
        session_timeout=int(status_dict.get('session_timeout', '60')),
        require_two_factor=status_dict.get('require_two_factor') == 'true',
        version=status_dict.get('version', '1.0.0'),
        maintenance_message=status_dict.get('maintenance_message', '系统正在维护，请稍后再试。')
    )
    
    if form.validate_on_submit():
        # 更新系统状态
        SystemStatus.query.filter_by(status_key='maintenance_mode').first().status_value = 'true' if form.maintenance_mode.data else 'false'
        SystemStatus.query.filter_by(status_key='login_attempts_limit').first().status_value = str(form.login_attempts_limit.data)
        SystemStatus.query.filter_by(status_key='account_lockout_duration').first().status_value = str(form.account_lockout_duration.data)
        SystemStatus.query.filter_by(status_key='default_security_level').first().status_value = str(form.default_security_level.data)
        SystemStatus.query.filter_by(status_key='session_timeout').first().status_value = str(form.session_timeout.data)
        SystemStatus.query.filter_by(status_key='require_two_factor').first().status_value = 'true' if form.require_two_factor.data else 'false'
        SystemStatus.query.filter_by(status_key='version').first().status_value = form.version.data
        SystemStatus.query.filter_by(status_key='maintenance_message').first().status_value = form.maintenance_message.data
        
        db.session.commit()
        log_system_event('admin', f'管理员 {current_user.username} 更新了系统配置', current_user.id, request.remote_addr)
        flash('系统配置已更新', 'success')
        return redirect(url_for('admin_system_status'))
    
    # 传递system_status给模板
    system_status = SystemStatus.query.all()
    return render_template('admin/system_status.html', form=form, system_status=system_status)

@app.route('/admin/logs')
@login_required
def admin_logs():
    if not current_user.is_admin:
        abort(403)
    
    page = request.args.get('page', 1, type=int)
    log_type = request.args.get('type')
    
    query = SystemLog.query
    if log_type:
        query = query.filter_by(log_type=log_type)
    
    logs = query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/logs.html', logs=logs, current_type=log_type)

@login_required
def admin_backup_data():
    if not current_user.is_admin:
        abort(403)
    
    # 这里是数据备份逻辑的占位符
    # 实际应用中应该实现数据库备份功能
    log_system_event('admin', f'管理员 {current_user.username} 执行了数据备份', current_user.id, request.remote_addr)
    flash('数据备份已完成', 'success')
    return redirect(url_for('admin_dashboard'))

@app.context_processor
def inject_sidebar_and_csp():
    ctx = {'csp_nonce': getattr(g, 'csp_nonce', '')}
    try:
        from datetime import datetime, timedelta
        # 仅在已登录且非登录/注册页时注入侧边栏数据
        if current_user.is_authenticated and request.endpoint not in ['login', 'register']:
            entries = DiaryEntry.query.filter_by(user_id=current_user.id) \
                .order_by(DiaryEntry.created_at.desc()).limit(50).all()
            today = datetime.utcnow().date()
            groups_map = {}
            for e in entries:
                d = e.created_at.date()
                if d == today:
                    label = '今天'
                elif d == today - timedelta(days=1):
                    label = '昨天'
                else:
                    label = d.strftime('%Y-%m-%d')
                groups_map.setdefault(label, []).append(e)
            # 按组里最新条目的时间降序排列分组
            sorted_groups = sorted(
                groups_map.items(),
                key=lambda kv: max(x.created_at for x in kv[1]),
                reverse=True
            )
            ctx['sidebar_groups'] = [{'label': k, 'items': v} for k, v in sorted_groups]
            
            # 添加管理员标志
            ctx['is_admin'] = current_user.is_admin
            
            # 添加安全等级信息
            ctx['security_level'] = current_user.security_level
            security_level_text = {1: '低', 2: '中', 3: '高'}
            ctx['security_level_text'] = security_level_text.get(current_user.security_level, '未知')
    except Exception:
        # 避免侧栏数据异常影响正常渲染
        pass
    return ctx

# 确保导入了所需的模块
from wtforms import BooleanField, SelectField
import secrets
import json

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # 初始化系统状态
        default_status = {
            'maintenance_mode': ('false', '系统维护模式'),
            'registration_open': ('true', '允许新用户注册'),
            'max_login_attempts': ('5', '最大登录尝试次数'),
            'session_timeout': ('3600', '会话超时时间（秒）'),
            'security_alert_level': ('normal', '安全警报级别')
        }
        
        for key, (value, desc) in default_status.items():
            status = SystemStatus.query.filter_by(status_key=key).first()
            if not status:
                status = SystemStatus(status_key=key, status_value=value, description=desc)
                db.session.add(status)
        
        # 创建默认管理员账户（仅在没有管理员时）
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                security_level=3
            )
            admin_user.set_password('Admin123456')  # 生产环境中应修改此密码
            db.session.add(admin_user)
            db.session.flush()  # 确保用户ID已生成
            
            # 为管理员创建安全配置
            admin_profile = SecurityProfile(user_id=admin_user.id)
            admin_profile.question = '系统默认安全问题'
            admin_profile.answer_hash = generate_password_hash('admin123')  # 生产环境中应修改
            db.session.add(admin_profile)
        
        db.session.commit()
    
    # 仅用于开发预览；部署时请用WSGI/ASGI服务器并启用HTTPS
    app.run(host='127.0.0.1', port=5000, debug=True)