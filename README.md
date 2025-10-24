# 日记Web应用 (Diary Web Application)

## 版本信息

**版本号**: v1.0.0
**最后更新**: 2024-10-25

## 项目介绍

这是一个基于Flask开发的个人日记Web应用，提供用户注册、登录、日记创建、编辑和管理等功能。应用采用了现代的Flask最佳实践，包括蓝图架构、表单验证、数据库ORM等，确保了应用的安全性、可扩展性和可维护性。

## 功能特点

- 用户注册与登录系统
- 安全的密码管理（哈希存储）
- 日记的增删改查操作
- 个人用户数据隔离
- 安全配置与防护措施（登录失败限制、账户锁定）
- 响应式设计，支持多种设备访问
- 密码找回功能
- RESTful API接口

## 技术栈

- **后端**: Flask 3.0.0
- **数据库**: SQLAlchemy 2.0 + MySQL
- **认证**: Flask-Login
- **表单处理**: Flask-WTF
- **请求限流**: Flask-Limiter
- **环境管理**: python-dotenv
- **测试**: pytest, coverage

## 安装说明

### 前置要求

- Python 3.8 或更高版本
- MySQL 数据库服务器
- Git（用于代码管理）

### 安装步骤

1. **克隆仓库**

   ```bash
   git clone [仓库URL]
   cd diary_web
   ```

2. **创建虚拟环境**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r diary_app/requirements.txt
   ```

4. **配置环境变量**

   在项目根目录创建`.env`文件，添加以下内容：

   ```
   # 数据库连接信息
   DATABASE_URL="mysql+pymysql://用户名:密码@localhost:3306/diary_db"

   # 应用密钥
   SECRET_KEY="your-secret-key-here"

   # 管理员用户列表（逗号分隔）
   ADMIN_USERS="admin"

   # 其他配置项
   FLASK_APP="diary_app.app"
   FLASK_ENV="development"
   ```

5. **初始化数据库**

   ```bash
   flask shell
   >>> from diary_app.extensions import db
   >>> db.create_all()
   >>> exit()
   ```

6. **运行应用**

   ```bash
   flask run
   ```

   访问 http://127.0.0.1:5000 开始使用应用。

## 使用说明

### 用户注册

1. 访问应用首页，点击"注册"链接
2. 填写用户名、邮箱和密码
3. 设置安全问题及答案
4. 点击"注册"按钮完成注册

### 用户登录

1. 访问应用首页，点击"登录"链接
2. 输入用户名和密码
3. 点击"登录"按钮

### 日记管理

#### 创建日记
1. 登录后，点击左侧菜单中的"新建日记"
2. 填写日记标题和内容
3. 点击"保存"按钮

#### 查看日记列表
1. 登录后，首页会显示您的所有日记
2. 可以按时间顺序查看日记

#### 查看日记详情
1. 在日记列表中点击任意日记标题
2. 进入日记详情页面查看完整内容

#### 编辑日记
1. 在日记详情页面，点击"编辑"按钮
2. 修改标题或内容
3. 点击"保存"按钮更新日记

#### 删除日记
1. 在日记详情页面，点击"删除"按钮
2. 在确认对话框中点击"确定"

### 个人设置

1. 点击右上角用户名，选择"个人设置"
2. 可以修改邮箱地址或密码
3. 点击"保存"按钮应用更改

### 密码找回

1. 在登录页面，点击"忘记密码"
2. 输入用户名并回答安全问题
3. 验证成功后设置新密码

## API文档

本应用提供了完整的RESTful API接口，详见[API文档](docs/api_documentation.md)。主要API包括：

- 用户认证：注册、登录、登出、密码重置
- 日记管理：创建、获取、更新、删除日记
- 用户信息：获取和更新用户信息

## 开发文档

### 数据库设计

数据库设计文档详见[数据库设计](docs/database_design.md)。主要包含以下表：

- users: 用户信息
- diary_entries: 日记条目
- security_profiles: 安全配置
- app_settings: 应用设置

### 代码规范

项目代码规范详见[代码规范](docs/coding_standards.md)。主要规范包括：

- Python代码遵循PEP 8
- 使用Google风格文档字符串
- 命名规范和类型提示
- HTML/CSS/JavaScript代码规范

### 测试

运行测试：

```bash
python -m pytest
```

生成测试覆盖率报告：

```bash
python -m pytest --cov=diary_app tests/
```

## 贡献指南

欢迎贡献代码或提出建议！请参阅[贡献指南](CONTRIBUTING.md)了解如何参与项目开发。

## 更新内容

### v1.0.0 (2024-10-25)

- 初始版本发布
- 实现用户注册、登录功能
- 实现日记的CRUD操作
- 添加安全配置和防护措施
- 提供RESTful API接口
- 添加完整的开发文档
- 实现单元测试覆盖

## 许可证

[MIT License](LICENSE)

## 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues
- 邮箱: [项目维护者邮箱]