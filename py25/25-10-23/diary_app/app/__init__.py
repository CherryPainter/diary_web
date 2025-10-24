"""应用初始化模块 - 实现应用工厂模式"""
import os
import pathlib
from flask import Flask
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从配置模块导入配置类
from app.config import config_by_name

# 从扩展模块导入扩展注册函数
from app.extensions import register_extensions, create_tables, db
from app.models.user import User


def create_app(config_name=None):
    """
    创建Flask应用实例的工厂函数
    
    Args:
        config_name: 配置名称，可选值: 'development', 'production', 'testing', 默认使用'development'
    
    Returns:
        Flask应用实例
    """
    import os
    # 如果没有提供配置名称，从环境变量获取或使用默认值
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    
    # 创建Flask应用实例，显式指定模板目录
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app = Flask(__name__, template_folder=template_dir, instance_relative_config=True)
    
    # 加载配置
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    # 确保 SECRET_KEY 在进程重启后保持一致，避免 CSRF session token 丢失
    # 优先使用环境变量 SECRET_KEY；若未提供，则在 instance 目录下维护一个持久化的 secret_key 文件
    try:
        if not os.getenv('SECRET_KEY'):
            instance_dir = pathlib.Path(app.instance_path)
            instance_dir.mkdir(parents=True, exist_ok=True)
            secret_file = instance_dir / 'secret_key'
            if secret_file.exists():
                app.config['SECRET_KEY'] = secret_file.read_text().strip()
            else:
                import secrets as _secrets
                key = _secrets.token_hex(32)
                secret_file.write_text(key)
                app.config['SECRET_KEY'] = key
    except Exception:
        # 如果任何原因无法读写实例目录，回退到框架默认（可能导致每次重启 secret 变化）
        pass
    
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
            # 开发环境回退（用于预览、无MySQL时）
            instance_dir = pathlib.Path(app.instance_path)
            instance_dir.mkdir(parents=True, exist_ok=True)
            DATABASE_URL = f"sqlite:///{instance_dir / 'diary.db'}"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # 确保上传文件夹存在
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # 注册扩展
    register_extensions(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 创建数据库表（如果不存在）
    with app.app_context():
        create_tables(app)
        # 确保有管理员用户
        ensure_admin_user()
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册请求钩子
    register_request_hooks(app)
    
    app.logger.info(f'应用初始化完成，配置环境: {config_name}')
    return app


def register_blueprints(app):
    """注册所有蓝图"""
    # 延迟导入以避免循环导入
    
    # 注册认证相关路由
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 注册日记相关路由
    from app.routes.diary_routes import diary_bp
    app.register_blueprint(diary_bp, url_prefix='/diary')
    
    # 注册用户相关路由
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')
    
    # 注册管理员相关路由
    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 注册主页路由
    try:
        from app.routes.main_routes import main_bp
        app.register_blueprint(main_bp)
    except ImportError:
        # 如果main_routes不存在，创建基本的主页路由
        from flask import render_template, redirect, url_for
        from flask_login import current_user
        
        @app.route('/')
        def index():
            """主页"""
            if current_user.is_authenticated:
                return redirect(url_for('diary.diary_list'))
            return redirect(url_for('auth.login'))
        
        # 静态页面路由
        @app.route('/about')
        def about():
            """关于页面"""
            return render_template('about.html')


def register_error_handlers(app):
    """注册错误处理器"""
    from flask import render_template
    
    @app.errorhandler(404)
    def page_not_found(error):
        """处理404错误"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """处理500错误"""
        app.logger.error('Internal Server Error: %s', str(error))
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理403错误"""
        return render_template('errors/403.html'), 403


def register_request_hooks(app):
    """注册请求钩子"""
    from flask import request, g
    from app.models.system import SystemStatus
    
    @app.before_request
    def before_request():
        """请求前的处理"""
        # 检查维护模式
        if app.config.get('MAINTENANCE_MODE'):
            # 允许管理员和特定路径访问
            if request.path.startswith('/static') or request.path.startswith('/auth/login'):
                return
            
            if hasattr(g, 'user') and g.user and g.user.is_admin:
                return
            
            from flask import render_template
            return render_template('maintenance.html'), 503
        
        # 记录请求信息（用于调试）
        if app.debug:
            app.logger.debug(f'请求路径: {request.path}, 方法: {request.method}, IP: {request.remote_addr}')
    
    @app.teardown_request
    def teardown_request(exception):
        """请求结束后的处理"""
        # 清理数据库会话
        if hasattr(g, 'db'):
            g.db.close()


def ensure_admin_user():
    """
    确保至少有一个管理员用户
    
    如果没有管理员用户，创建一个默认管理员
    """
    # 检查是否已有管理员
    admin_user = User.query.filter_by(is_admin=True).first()
    
    # 如果没有管理员，创建一个默认管理员
    if not admin_user and not User.query.first():
        # 只在没有任何用户时创建默认管理员
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            security_level=3
        )
        admin.set_password('admin123456')  # 设置默认密码（生产环境应更改）
        
        from app.models import SecurityProfile
        security_profile = SecurityProfile(
            user_id=admin.id,
            question='默认管理员安全问题',
            failed_count=0
        )
        from werkzeug.security import generate_password_hash
        security_profile.answer_hash = generate_password_hash('adminanswer')
        
        db.session.add(admin)
        db.session.add(security_profile)
        db.session.commit()
        
        print("已创建默认管理员账户")
        print("用户名: admin")
        print("密码: admin123456")
        print("请在首次登录后立即更改密码！")