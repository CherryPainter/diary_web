import click
from diary_app import create_app
import os

def main():
    """日记Web应用的命令行入口"""
    app = create_app(config_name=os.environ.get('FLASK_ENV', 'development'))
    
    @app.cli.command("init-db")
    def init_db():
        """初始化数据库"""
        from diary_app.extensions import db
        from diary_app.models import User, DiaryEntry, SecurityProfile, AppSetting
        
        click.echo("删除现有数据库表...")
        db.drop_all()
        
        click.echo("创建数据库表...")
        db.create_all()
        
        click.echo("初始化默认设置...")
        # 创建默认应用设置
        default_settings = [
            AppSetting(key='site_name', value='日记Web应用'),
            AppSetting(key='site_description', value='一个简单而安全的个人日记应用'),
            AppSetting(key='max_entries_per_page', value='10'),
            AppSetting(key='login_attempts_limit', value='5'),
            AppSetting(key='lockout_duration_minutes', value='30'),
        ]
        
        for setting in default_settings:
            db.session.add(setting)
        
        db.session.commit()
        click.echo("数据库初始化完成！")
    
    @app.cli.command("create-admin")
    @click.argument("username")
    @click.password_option()
    @click.option("--email", prompt="Admin email")
    @click.option("--question", prompt="Security question")
    @click.password_option("--answer", confirmation_prompt=False, prompt="Security answer")
    def create_admin(username, password, email, question, answer):
        """创建管理员用户"""
        from diary_app.models import User, SecurityProfile
        from werkzeug.security import generate_password_hash
        
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            click.echo(f"错误: 用户 '{username}' 已存在")
            return
        
        # 创建管理员用户
        admin_user = User(username=username, email=email, is_admin=True)
        admin_user.set_password(password)
        
        # 创建安全配置文件
        security_profile = SecurityProfile(
            user=admin_user,
            question=question,
            answer_hash=generate_password_hash(answer)
        )
        
        from diary_app.extensions import db
        db.session.add(admin_user)
        db.session.add(security_profile)
        db.session.commit()
        
        click.echo(f"管理员用户 '{username}' 创建成功！")
    
    @app.cli.command("run-dev")
    @click.option("--host", default="127.0.0.1", help="主机地址")
    @click.option("--port", default=5000, help="端口号")
    def run_dev(host, port):
        """运行开发服务器"""
        app.run(host=host, port=port, debug=True)
    
    # 运行Flask命令行接口
    app.cli()

if __name__ == "__main__":
    main()