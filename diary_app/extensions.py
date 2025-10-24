from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Flask extensions singletons

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=[])

__all__ = [
    "db",
    "login_manager",
    "csrf",
    "limiter",
]