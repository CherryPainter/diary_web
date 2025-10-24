from flask import Blueprint, jsonify, request, abort, current_app
from flask_login import login_required, current_user

from ..services.admin_service import AdminService
from ..repositories.user_repo import UserRepository
from ..repositories.diary_repo import DiaryRepository
from ..models import User, DiaryEntry

bp_admin = Blueprint('admin', __name__, url_prefix='/admin')

_admin_service = None

def get_admin_service():
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService(UserRepository(), DiaryRepository(), admin_users=current_app.config.get('ADMIN_USERS', set()))
    return _admin_service


def require_admin():
    service = get_admin_service()
    if not current_user.is_authenticated or not service.is_admin(current_user.username):
        abort(403)

@bp_admin.route('/api/users', methods=['GET'])
@login_required
def api_list_users():
    require_admin()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = get_admin_service().list_users(page=page, per_page=per_page)
    return jsonify({
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'items': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'created_at': u.created_at.isoformat(),
                'locked': bool(u.security_profile and ((u.security_profile.failed_count or 0) >= 3)),
            } for u in pagination.items
        ]
    })

@bp_admin.route('/api/users/<int:user_id>/lock', methods=['POST'])
@login_required
def api_lock_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    ok, msg = get_admin_service().lock_user(user)
    return jsonify({'ok': ok, 'message': msg})

@bp_admin.route('/api/users/<int:user_id>/unlock', methods=['POST'])
@login_required
def api_unlock_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    ok, msg = get_admin_service().unlock_user(user)
    return jsonify({'ok': ok, 'message': msg})

@bp_admin.route('/api/entries', methods=['GET'])
@login_required
def api_list_entries():
    require_admin()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    pagination = get_admin_service().list_entries(page=page, per_page=per_page, user_id=user_id)
    return jsonify({
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'items': [
            {
                'id': e.id,
                'user_id': e.user_id,
                'title': e.title,
                'created_at': e.created_at.isoformat(),
                'updated_at': e.updated_at.isoformat(),
            } for e in pagination.items
        ]
    })

@bp_admin.route('/api/entries/<int:entry_id>', methods=['DELETE'])
@login_required
def api_delete_entry(entry_id):
    require_admin()
    entry = DiaryEntry.query.get_or_404(entry_id)
    ok, msg = get_admin_service().delete_entry(entry)
    return jsonify({'ok': ok, 'message': msg})