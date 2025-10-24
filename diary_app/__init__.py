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

    # Preserve legacy endpoint names used in templates
    vf = app.view_functions
    aliases = {
        'index': 'main.index',
        'register': 'main.register',
        'login': 'main.login',
        'logout': 'main.logout',
        'create_entry': 'main.create_entry',
        'edit_entry': 'main.edit_entry',
        'delete_entry': 'main.delete_entry',
        'aux_verify': 'main.aux_verify',
        'settings': 'main.settings',
    }
    for alias, target in aliases.items():
        vf[alias] = vf[target]

    with app.app_context():
        db.create_all()

    return app