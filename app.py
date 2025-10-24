from simple_notes import create_app
import os

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    # 获取环境变量中的配置
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # 启动应用服务器
    print(f"启动简笔记应用服务器...")
    print(f"访问地址: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)