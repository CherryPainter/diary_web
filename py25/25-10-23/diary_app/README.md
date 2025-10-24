# 日记应用 (Diary App)

一个基于Flask框架开发的安全、可持续、可维护的日记应用，采用模块化、面向对象的设计架构。

## 项目特点

- **安全可靠**：实现了多层安全机制，包括密码哈希存储、账户锁定、安全等级设置等
- **模块化架构**：采用面向对象和模块化设计，便于维护和扩展
- **完整功能**：支持日记的创建、编辑、删除、搜索，以及用户认证、权限管理等
- **响应式设计**：适配不同设备的显示
- **管理功能**：提供完善的管理员界面，用于用户管理和系统配置
- **日志记录**：记录系统事件和安全日志，便于追踪和审计

## 技术栈

- **后端框架**: Flask 3.0.0
- **ORM**: SQLAlchemy 2.0.32, Flask-SQLAlchemy 3.1.1
- **认证**: Flask-Login 0.6.3
- **表单处理**: Flask-WTF 1.2.1, WTForms
- **安全特性**: Flask-Limiter 3.6.0（限流），Flask-CSRFProtect
- **数据库**: MySQL (生产环境)，SQLite（开发环境）
- **环境管理**: python-dotenv 1.0.1
- **前端**: HTML5, CSS3, JavaScript, Bootstrap

## 安装与配置

### 1. 克隆项目

```bash
git clone <项目仓库地址>
cd diary_app
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制`.env.example`文件为`.env`并填写实际配置：

```bash
cp .env.example .env
```

编辑`.env`文件，设置以下关键配置：

- **数据库配置**：可以使用MySQL（推荐生产环境）或SQLite（开发环境）
- **SECRET_KEY**：设置为随机生成的长字符串
- **FLASK_CONFIG**：设置运行环境（development/production/testing）
- **LOGIN_RATE_LIMIT**：配置登录请求的限流规则

### 5. 初始化数据库

启动应用时，系统会自动创建所需的数据库表结构：

```bash
python app.py
```

系统首次运行会自动创建默认管理员账户：
- 用户名：`admin`
- 密码：`admin123456`
- 安全问题：`默认管理员安全问题`
- 安全答案：`adminanswer`

> **重要安全提示**：生产环境部署前请立即修改这些默认凭据！

## 项目结构

项目采用模块化架构设计，遵循关注点分离原则，使代码更加清晰、可维护和可扩展。主要模块包括：

```
diary_app/
├── app/                      # 主应用包
│   ├── __init__.py           # 应用初始化（工厂模式）
│   ├── config.py             # 配置管理（环境特定配置）
│   ├── extensions.py         # 扩展初始化
│   ├── models/               # 数据模型
│   │   ├── __init__.py       # 模型导出
│   │   ├── user.py           # 用户相关模型
│   │   ├── diary.py          # 日记相关模型
│   │   └── system.py         # 系统相关模型
│   ├── forms/                # 表单定义
│   │   ├── __init__.py       # 表单导出
│   │   ├── auth.py           # 认证相关表单
│   │   ├── diary.py          # 日记相关表单
│   │   └── admin.py          # 管理员相关表单
│   ├── services/             # 业务逻辑层
│   │   ├── __init__.py       # 服务导出
│   │   ├── auth_service.py   # 认证服务
│   │   ├── user_service.py   # 用户服务
│   │   ├── diary_service.py  # 日记服务
│   │   ├── system_service.py # 系统服务
│   │   └── admin_service.py  # 管理员服务
│   ├── routes/               # 路由处理
│   │   ├── __init__.py       # 路由导出
│   │   ├── auth_routes.py    # 认证相关路由
│   │   ├── diary_routes.py   # 日记相关路由
│   │   ├── user_routes.py    # 用户相关路由
│   │   └── admin_routes.py   # 管理员相关路由
│   └── utils/                # 工具函数
│       ├── __init__.py       # 工具导出
│       ├── security.py       # 安全相关工具
│       ├── logging.py        # 日志工具
│       ├── email.py          # 邮件工具
│       └── data.py           # 数据处理工具
├── app.py                    # 应用入口（简化）
├── requirements.txt          # 项目依赖
├── .env.example              # 环境变量示例
├── README.md                 # 项目文档
├── static/                   # 静态资源文件
│   ├── css/                  # CSS样式文件
│   └── js/                   # JavaScript文件
├── templates/                # HTML模板
│   ├── admin/                # 管理员后台模板
│   ├── errors/               # 错误页面模板
│   └── *.html                # 主要页面模板
└── instance/                 # 实例相关文件（如SQLite数据库）
```

## 系统架构说明

### 1. 模块化设计

项目采用模块化设计，将不同功能的代码分离到不同的包中，实现关注点分离：

- **models**: 定义数据结构和数据库模型
- **forms**: 定义表单验证和处理逻辑
- **services**: 封装业务逻辑，处理复杂的业务操作
- **routes**: 处理HTTP请求和响应
- **utils**: 提供通用工具函数

### 2. 服务层设计

服务层作为业务逻辑的核心，提供了对数据库操作的封装，实现了业务规则和数据访问的分离。主要服务包括：

- **认证服务**：处理用户注册、登录、登出等操作
- **用户服务**：管理用户信息、密码修改、安全设置等
- **日记服务**：提供日记的CRUD操作和搜索功能
- **系统服务**：管理系统状态、配置和统计信息
- **管理员服务**：提供管理员特定的操作功能

### 3. 配置管理

项目支持多环境配置（开发、测试、生产），通过环境变量选择不同的配置：

- **BaseConfig**: 基础配置，包含所有环境共用的设置
- **DevelopmentConfig**: 开发环境配置，启用调试模式
- **ProductionConfig**: 生产环境配置，优化性能和安全性
- **TestingConfig**: 测试环境配置，使用测试数据库

## 数据库模型

### 1. User（用户模型）
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    security_level = db.Column(db.Integer, default=1, nullable=False)  # 1-低, 2-中, 3-高

    diaries = db.relationship('DiaryEntry', backref='user', lazy=True, cascade="all, delete-orphan")
```

### 2. DiaryEntry（日记条目）

```python
class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### 3. SecurityProfile（安全配置）

```python
class SecurityProfile(db.Model):
    __tablename__ = 'security_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    question = db.Column(db.String(255))
    answer_hash = db.Column(db.String(255))
    failed_count = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # 增强的安全特性
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    recovery_codes = db.Column(db.Text, nullable=True)
    last_password_change = db.Column(db.DateTime, nullable=True)
    password_history = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('security_profile', uselist=False, cascade="all, delete-orphan"))
```

### 4. SystemStatus（系统状态）

```python
class SystemStatus(db.Model):
    __tablename__ = 'system_status'
    id = db.Column(db.Integer, primary_key=True)
    status_key = db.Column(db.String(50), unique=True, nullable=False)
    status_value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### 5. SystemLog（系统日志）

```python
class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50), nullable=False)  # 'info', 'warning', 'error', 'security'
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref='logs')
```

## 路由与功能

### 1. 用户认证

- `GET/POST /register` - 用户注册
- `GET/POST /login` - 用户登录
- `GET /logout` - 用户登出

### 2. 日记管理

- `GET /` - 查看日记列表
- `GET/POST /entry/new` - 创建新日记
- `GET/POST /entry/<int:entry_id>/edit` - 编辑日记
- `POST /entry/<int:entry_id>/delete` - 删除日记

### 3. 用户设置

- `GET/POST /settings` - 用户设置页面，包含密码修改、安全设置和安全等级管理
- `POST /login/aux-verify` - 辅助验证解锁账户
- `GET/POST /verify-security` - 安全验证页面

### 4. 管理员功能

- `GET /admin/dashboard` - 管理员仪表盘
- `GET /admin/users` - 用户列表管理
- `GET/POST /admin/user/<int:user_id>/edit` - 编辑用户信息
- `GET/POST /admin/system-status` - 系统状态配置
- `GET /admin/logs` - 系统日志查看

## 安全特性

### 1. 安全等级

应用支持三个安全等级，不同等级有不同的安全要求：

- **低等级** (1): 基础安全措施
- **中等级** (2): 要求密码包含大小写字母和数字
- **高等级** (3): 除中等级要求外，敏感操作（修改密码、删除日记等）需要额外安全验证

### 2. 账户安全

- **密码哈希存储**：使用 Werkzeug 的 generate_password_hash 存储密码
- **登录尝试限制**：多次失败后账户锁定，需辅助验证解锁
- **密码历史记录**：防止重复使用最近的密码
- **会话管理**：支持会话超时配置

### 3. 请求限流

使用 Flask-Limiter 限制登录请求频率，防止暴力破解。

### 4. 安全响应头

应用设置了多种安全响应头：

- Content-Security-Policy
- X-Content-Type-Options
- X-Frame-Options
- Referrer-Policy

### 5. CSRF 保护

使用 Flask-WTF 的 CSRFProtect 保护表单提交。

## 管理员功能详解

### 1. 仪表盘

展示系统概览信息：
- 用户统计（总用户数、活跃用户数）
- 日记统计（总条目数）
- 最新系统日志
- 最新日记条目

### 2. 用户管理

- 查看所有用户列表
- 编辑用户信息（用户名、邮箱、管理员权限、安全等级）
- 保护机制：管理员不能编辑其他管理员账户

### 3. 系统状态配置

管理员可以配置以下系统参数：

- 维护模式开关
- 登录尝试限制次数
- 账户锁定时长（分钟）
- 默认安全等级
- 会话超时时间（分钟）
- 双因素认证要求
- 系统版本
- 维护消息内容

### 4. 系统日志

查看和筛选系统日志：
- 支持按日志类型筛选（info、warning、error、security）
- 记录详细的操作信息，包括操作用户、IP地址和时间

## 部署注意事项

### 1. 生产环境配置

- **使用生产级WSGI服务器**：如 Gunicorn、uWSGI
- **配置HTTPS**：确保所有通信加密
- **数据库选择**：使用MySQL代替SQLite
- **修改默认凭据**：首次部署后立即修改默认管理员账户的密码和安全问题

### 2. 安全增强

- **配置持久化限流存储**：Flask-Limiter 默认使用内存存储，生产环境应配置 Redis 等持久化存储
- **定期备份数据库**：确保数据安全
- **监控系统日志**：及时发现异常行为

## 开发指南

### 1. 添加新功能

1. **模型扩展**：在 `app.py` 中扩展现有模型或添加新模型
2. **表单定义**：使用 WTForms 定义新表单类
3. **路由实现**：添加新的视图函数处理请求
4. **模板创建**：在 `templates/` 目录下创建对应的HTML模板

### 2. 调试

- 开发模式下，Flask 提供自动重载功能
- 错误页面位于 `templates/errors/` 目录
- 系统日志可在管理员日志页面查看

### 3. 代码风格

- 遵循 PEP 8 编码规范
- 使用类型提示增强代码可读性
- 为关键功能添加适当的注释

## 故障排除

### 数据库错误

如果遇到数据库相关错误，尝试删除 `instance/diary.db` 文件并重新启动应用，系统会重新创建数据库结构。

### 依赖问题

确保使用正确版本的依赖包，可参考 `requirements.txt` 文件中的版本号。

### 安全令牌问题

如果高安全级别操作出现问题，检查用户是否已完成安全验证，以及安全令牌是否有效。

## 许可证

[此处可添加项目许可证信息]

---

**最后更新时间**: 2023-10-25
**版本**: 1.0.0