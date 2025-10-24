import os
import pathlib
from datetime import datetime, timedelta

from flask import Flask, render_template, redirect, url_for, flash, request, abort, g
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf import CSRFProtect
import mimetypes
import secrets
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')


# 加载 .env
load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect(app)

# 安全配置
secret_key = os.getenv("SECRET_KEY") or os.urandom(32)
app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# 若启用HTTPS，可设置为True
app.config["SESSION_COOKIE_SECURE"] = False

# 数据库配置：优先 DATABASE_URL，其次 MySQL 环境变量，最后开发用 SQLite 回退
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    if MYSQL_HOST and MYSQL_DB and MYSQL_USER and MYSQL_PASSWORD:
        DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    else:
        # 开发环境回退（用于预览、无MySQL时），实际部署请配置MySQL
        instance_dir = pathlib.Path(app.instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        DATABASE_URL = f"sqlite:///{instance_dir / 'diary.db'}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化数据库
db = SQLAlchemy(app)

# 登录管理与限流
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "请先登录再访问该页面。"

login_rate_limit = os.getenv("LOGIN_RATE_LIMIT", "10 per minute")
limiter = Limiter(get_remote_address, app=app, default_limits=[])

# 模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    diaries = db.relationship('DiaryEntry', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SecurityProfile(db.Model):
    __tablename__ = 'security_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    question = db.Column(db.String(255))
    answer_hash = db.Column(db.String(255))
    failed_count = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref=db.backref('security_profile', uselist=False, cascade="all, delete-orphan"))

# 表单
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

class DiaryForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('内容', validators=[DataRequired(), Length(max=10000)])
    submit = SubmitField('保存')

# 登录回调
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
        return redirect(url_for('index'))
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
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit(lambda: login_rate_limit)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

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
        login_user(user)
        db.session.commit()
        flash('登录成功', 'success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('index'))
    return render_template('login.html', form=form, locked_user=locked_user, security_question=security_question)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/entry/new', methods=['GET', 'POST'])
@login_required
def create_entry():
    form = DiaryForm()
    if form.validate_on_submit():
        entry = DiaryEntry(user_id=current_user.id, title=form.title.data.strip(), content=form.content.data)
        db.session.add(entry)
        db.session.commit()
        flash('日记已创建', 'success')
        return redirect(url_for('index'))
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
        return redirect(url_for('index'))
    return render_template('entry_form.html', form=form, mode='edit')

@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = DiaryEntry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        abort(404)
    db.session.delete(entry)
    db.session.commit()
    flash('日记已删除', 'info')
    return redirect(url_for('index'))

@app.route('/login/aux-verify', methods=['POST'])
def aux_verify():
    username = request.form.get('username', '').strip()
    answer = request.form.get('answer', '')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('login'))
    profile = user.security_profile
    if not profile or not profile.question or not profile.answer_hash:
        flash('未设置辅助验证，无法解锁。', 'danger')
        return redirect(url_for('login', u=username))
    if not check_password_hash(profile.answer_hash, answer):
        flash('辅助验证答案错误。', 'danger')
        return redirect(url_for('login', u=username))
    # 验证通过，解除锁定
    profile.failed_count = 0
    profile.locked_until = None
    db.session.commit()
    flash('账户已解锁，请重新登录。', 'success')
    return redirect(url_for('login', u=username))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile = current_user.security_profile
    if not profile:
        profile = SecurityProfile(user_id=current_user.id, failed_count=0)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        form_name = request.form.get('form')
        if form_name == 'password':
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new = request.form.get('confirm_new', '')
            if not current_user.check_password(old_password):
                flash('旧密码错误', 'danger')
            elif not new_password or len(new_password) < 8:
                flash('新密码长度至少8位', 'danger')
            elif new_password != confirm_new:
                flash('两次输入的新密码不一致', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('密码已更新', 'success')
                return redirect(url_for('settings') + '#password')
        elif form_name == 'security':
            question = request.form.get('question', '').strip()
            answer = request.form.get('answer', '')
            if not question or not answer:
                flash('请填写问题和答案', 'danger')
            else:
                profile.question = question
                profile.answer_hash = generate_password_hash(answer)
                db.session.commit()
                flash('辅助验证已保存', 'success')
                return redirect(url_for('settings') + '#security')

    return render_template('settings.html', profile=profile)

# 错误页
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

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
    except Exception:
        # 避免侧栏数据异常影响正常渲染
        pass
    return ctx

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # 仅用于开发预览；部署时请用WSGI/ASGI服务器并启用HTTPS
    app.run(host='127.0.0.1', port=5000, debug=True)