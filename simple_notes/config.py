import os
import pathlib
from dotenv import load_dotenv
import simple_notes

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # enable True when using HTTPS

    LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "10 per minute")

    @staticmethod
    def build_database_url(instance_path: str) -> str:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url
        mysql_host = os.getenv("MYSQL_HOST")
        mysql_port = os.getenv("MYSQL_PORT", "3306")
        mysql_db = os.getenv("MYSQL_DB")
        mysql_user = os.getenv("MYSQL_USER")
        mysql_password = os.getenv("MYSQL_PASSWORD")
        if mysql_host and mysql_db and mysql_user and mysql_password:
            return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
        # fallback to sqlite for dev/preview
        instance_dir = pathlib.Path(instance_path)
        instance_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{instance_dir / 'notes.db'}"

    @classmethod
    def apply(cls, app):
        app.config["SECRET_KEY"] = cls.SECRET_KEY
        app.config["SESSION_COOKIE_HTTPONLY"] = cls.SESSION_COOKIE_HTTPONLY
        app.config["SESSION_COOKIE_SAMESITE"] = cls.SESSION_COOKIE_SAMESITE
        app.config["SESSION_COOKIE_SECURE"] = cls.SESSION_COOKIE_SECURE

        db_url = cls.build_database_url(app.instance_path)
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        app.config["LOGIN_RATE_LIMIT"] = cls.LOGIN_RATE_LIMIT

        # Admin settings via env: comma-separated usernames
        admin_users = set(
            u.strip() for u in os.getenv("ADMIN_USERS", "").split(",") if u.strip()
        )
        if not admin_users:
            admin_users = {"admin"}
        app.config["ADMIN_USERS"] = admin_users
        app.config["ADMIN_DEFAULT_PASSWORD"] = os.getenv("ADMIN_DEFAULT_PASSWORD", "ChangeMe123!")