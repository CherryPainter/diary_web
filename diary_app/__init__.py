from flask import Flask

from .extensions import db, login_manager, csrf, limiter
from .config import Config
from .security import set_csp_nonce, set_security_headers
from .blueprints.main import bp as main_bp
from .blueprints.admin import bp_admin as admin_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Apply config
    Config.apply(app)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Security hooks
    app.before_request(set_csp_nonce)
    app.after_request(set_security_headers)

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Preserve legacy endpoint names used in templates by adding alias URL rules
    vf = app.view_functions
    alias_rules = [
        ('/', 'index', 'main.index', ['GET']),
        ('/register', 'register', 'main.register', ['GET', 'POST']),
        ('/login', 'login', 'main.login', ['GET', 'POST']),
        ('/logout', 'logout', 'main.logout', ['GET']),
        ('/entry/new', 'create_entry', 'main.create_entry', ['GET', 'POST']),
        ('/entry/<int:entry_id>/edit', 'edit_entry', 'main.edit_entry', ['GET', 'POST']),
        ('/entry/<int:entry_id>/delete', 'delete_entry', 'main.delete_entry', ['POST']),
        ('/login/aux-verify', 'aux_verify', 'main.aux_verify', ['POST']),
        ('/settings', 'settings', 'main.settings', ['GET', 'POST']),
    ]
    for rule, endpoint, target, methods in alias_rules:
        app.add_url_rule(rule, endpoint=endpoint, view_func=vf[target], methods=methods)

    with app.app_context():
        db.create_all()
        # Bootstrap default admin(s) and persist admin list
        try:
            from .services.admin_service import AdminService
            from .models import User, AppSetting
            from werkzeug.security import generate_password_hash
            # Persist initial admin list if not set yet
            if not AppSetting.query.filter_by(key='admin_users').first():
                initial_admins = set(app.config.get('ADMIN_USERS', set()))
                if initial_admins:
                    AdminService().set_admin_users(initial_admins)
            admin_users = AdminService().get_admin_users()
            default_pw = app.config.get('ADMIN_DEFAULT_PASSWORD', 'ChangeMe123!')
            for uname in admin_users:
                if not User.query.filter_by(username=uname).first():
                    u = User(username=uname, email=f"{uname}@local", password_hash=generate_password_hash(default_pw))
                    db.session.add(u)
            db.session.commit()
        except Exception:
            # Avoid startup failure due to bootstrap issues; log in server output
            import traceback
            traceback.print_exc()

    return app