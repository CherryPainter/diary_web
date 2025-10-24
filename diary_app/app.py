from diary_app import create_app

app = create_app()

if __name__ == '__main__':
    # 仅用于开发预览；部署请使用 WSGI/ASGI 服务器并启用 HTTPS
    app.run(host='127.0.0.1', port=5000, debug=True)