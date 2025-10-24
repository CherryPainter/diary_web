from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, g, current_app
from flask_login import login_user, login_required, logout_user, current_user, UserMixin

from ..extensions import db, login_manager, limiter
from ..forms import RegisterForm, LoginForm, DiaryForm
from ..models import User, DiaryEntry
from ..services.auth_service import AuthService
from ..services.diary_service import DiaryService

bp = Blueprint('main', __name__)
auth_service = AuthService()
diary_service = DiaryService()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    flash('请先登录再访问该页面。', 'warning')
    return redirect(url_for('main.login'))

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = diary_service.repo.list_of_user_paginated(current_user.id, page=page, per_page=10)
    return render_template('index.html', pagination=pagination, entries=pagination.items)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        ok, msg, _user = auth_service.register(form.username.data, form.email.data, form.password.data)
        if not ok:
            flash(msg, 'danger')
            return render_template('register.html', form=form)
        flash(msg, 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit(lambda: current_app.config.get('LOGIN_RATE_LIMIT', '10 per minute'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    username_param = request.args.get('u')
    locked_user = None
    security_question = None
    if username_param:
        u = User.query.filter_by(username=username_param.strip()).first()
        if u and u.security_profile and ((u.security_profile.locked_until and u.security_profile.locked_until > datetime.utcnow()) or (u.security_profile.failed_count or 0) >= 3):
            locked_user = u.username
            security_question = u.security_profile.question

    form = LoginForm()
    if form.validate_on_submit():
        ok, msg, user, sec_q = auth_service.validate_login(form.username.data, form.password.data)
        if not ok:
            category = 'warning' if '锁定' in msg else 'danger'
            flash(msg, category)
            return render_template('login.html', form=form, locked_user=locked_user or (user.username if user else None), security_question=sec_q or security_question)
        login_user(user)
        flash('登录成功', 'success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('main.index'))
    return render_template('login.html', form=form, locked_user=locked_user, security_question=security_question)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('main.login'))

@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def create_entry():
    form = DiaryForm()
    if form.validate_on_submit():
        ok, msg, _entry = diary_service.create_entry(current_user.id, form.title.data, form.content.data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('main.index'))
    return render_template('entry_form.html', form=form, mode='create')

@bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = diary_service.repo.get_by_id_for_user(entry_id, current_user.id)
    if not entry:
        abort(404)
    form = DiaryForm(obj=entry)
    if form.validate_on_submit():
        ok, msg = diary_service.update_entry(entry, form.title.data, form.content.data)
        flash(msg, 'success' if ok else 'danger')
        if ok:
            return redirect(url_for('main.index'))
    return render_template('entry_form.html', form=form, mode='edit')

@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = diary_service.repo.get_by_id_for_user(entry_id, current_user.id)
    if not entry:
        abort(404)
    ok, msg = diary_service.delete_entry(entry)
    flash(msg, 'info' if ok else 'danger')
    return redirect(url_for('main.index'))

@bp.route('/login/aux-verify', methods=['POST'])
def aux_verify():
    username = request.form.get('username', '').strip()
    answer = request.form.get('answer', '')
    ok, msg = auth_service.aux_verify(username, answer)
    flash(msg, 'success' if ok else 'danger')
    return redirect(url_for('main.login', u=username))

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile = current_user.security_profile
    if not profile:
        profile = auth_service.user_repo.ensure_profile(current_user)
    if request.method == 'POST':
        form_name = request.form.get('form')
        if form_name == 'password':
            ok, msg = auth_service.change_password(
                current_user,
                request.form.get('old_password', ''),
                request.form.get('new_password', ''),
                request.form.get('confirm_new', ''),
            )
            flash(msg, 'success' if ok else 'danger')
            if ok:
                return redirect(url_for('main.settings') + '#password')
        elif form_name == 'security':
            ok, msg = auth_service.save_security(
                current_user,
                request.form.get('question', ''),
                request.form.get('answer', ''),
                request.form.get('auth_password', ''),
            )
            flash(msg, 'success' if ok else 'danger')
            if ok:
                return redirect(url_for('main.settings') + '#security')
    return render_template('settings.html', profile=profile)

@bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

@bp.app_context_processor
def inject_sidebar_and_csp():
    ctx = {'csp_nonce': getattr(g, 'csp_nonce', '')}
    try:
        if current_user.is_authenticated and request.endpoint not in ['main.login', 'main.register']:
            entries = diary_service.repo.recent_entries(current_user.id, limit=50)
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
            sorted_groups = sorted(
                groups_map.items(),
                key=lambda kv: max(x.created_at for x in kv[1]),
                reverse=True
            )
            ctx['sidebar_groups'] = [{'label': k, 'items': v} for k, v in sorted_groups]
    except Exception:
        pass
    return ctx