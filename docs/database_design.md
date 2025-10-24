# 数据库设计文档

## 1. 数据库概述

本项目使用 SQLAlchemy 作为 ORM 工具，MySQL 作为底层数据库。数据库设计遵循关系型数据库的最佳实践，包括主键外键约束、索引优化等。

## 2. 数据库表结构

### 2.1 users 表

**用途**：存储用户基本信息

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTO_INCREMENT` | 用户唯一标识符 |
| `username` | `VARCHAR(50)` | `UNIQUE, NOT NULL` | 用户名，用于登录 |
| `email` | `VARCHAR(120)` | `UNIQUE, NOT NULL` | 用户邮箱 |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | 密码哈希值，使用 Werkzeug 安全哈希 |
| `created_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | 用户创建时间 |

**索引**：
- `id` (主键索引)
- `username` (唯一索引)
- `email` (唯一索引)

**关系**：
- 一对多：一个用户可以有多个日记条目
- 一对一：一个用户可以有一个安全配置文件

### 2.2 diary_entries 表

**用途**：存储用户的日记内容

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTO_INCREMENT` | 日记条目唯一标识符 |
| `user_id` | `INTEGER` | `NOT NULL, FOREIGN KEY (users.id)` | 所属用户ID |
| `title` | `VARCHAR(200)` | `NOT NULL` | 日记标题 |
| `content` | `TEXT` | `NOT NULL` | 日记内容 |
| `created_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | 创建时间 |
| `updated_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新时间 |

**索引**：
- `id` (主键索引)
- `user_id` (外键索引，用于加速按用户查询)
- `created_at` (索引，用于按时间排序)

**关系**：
- 多对一：多个日记条目属于一个用户

### 2.3 security_profiles 表

**用途**：存储用户安全相关配置和登录安全信息

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY, AUTO_INCREMENT` | 安全配置文件唯一标识符 |
| `user_id` | `INTEGER` | `NOT NULL, UNIQUE, FOREIGN KEY (users.id)` | 所属用户ID |
| `question` | `VARCHAR(255)` | `NOT NULL` | 安全问题 |
| `answer_hash` | `VARCHAR(255)` | `NOT NULL` | 安全问题答案的哈希值 |
| `failed_count` | `INTEGER` | `NOT NULL, DEFAULT 0` | 登录失败次数 |
| `locked_until` | `DATETIME` | `NULL` | 账户锁定截止时间 |

**索引**：
- `id` (主键索引)
- `user_id` (外键索引，唯一约束)

**关系**：
- 一对一：一个安全配置文件属于一个用户

### 2.4 app_settings 表

**用途**：存储应用程序级别的设置

| 字段名 | 数据类型 | 约束 | 描述 |
| :--- | :--- | :--- | :--- |
| `key` | `VARCHAR(50)` | `PRIMARY KEY` | 设置键名 |
| `value` | `TEXT` | `NOT NULL` | 设置值 |

**索引**：
- `key` (主键索引)

## 3. 实体关系图 (ERD)

```
+-------------+      +------------------+      +----------------+      +------------------+
|             |      |                  |      |                |      |                  |
|    users    |<---->|  diary_entries   |      | security_profiles|<---->|       users      |
|             |      |                  |      |                |      |                  |
+-------------+      +------------------+      +----------------+      +------------------+
        ^                                                                   ^
        |                                                                   |
        |                                                                   |
+-------------+                                                             |
|             |                                                             |
| app_settings|<-------------------------------------------------------------+
|             |
+-------------+
```

## 4. 数据库连接配置

数据库连接通过环境变量配置，格式如下：

```
DATABASE_URL="mysql+pymysql://用户名:密码@localhost:3306/diary_db"
```

## 5. 索引优化

1. **users表**：
   - `username` 和 `email` 字段添加唯一索引，加速登录查询
   - `created_at` 字段添加索引，用于用户注册统计

2. **diary_entries表**：
   - `user_id` 字段添加索引，加速用户日记查询
   - `created_at` 字段添加索引，加速按时间排序和筛选
   - 复合索引 `(user_id, created_at)` 可进一步优化用户日记时间排序查询

3. **security_profiles表**：
   - `user_id` 字段添加唯一索引，确保一对一关系并加速查询
   - `locked_until` 字段可考虑添加索引，用于检查锁定状态

## 6. 数据安全考虑

1. **密码安全**：
   - 密码使用 Werkzeug 的 `generate_password_hash` 方法进行哈希存储
   - 不存储明文密码，防止数据库泄露导致密码泄露

2. **数据隔离**：
   - 用户只能访问自己的日记数据
   - 通过 `user_id` 外键约束确保数据归属正确

3. **账户安全**：
   - `failed_count` 和 `locked_until` 字段用于实现登录失败锁定机制
   - 安全问题和答案用于密码重置功能

## 7. 数据库迁移策略

使用 Flask-Migrate 进行数据库版本控制和迁移：

```bash
# 初始化迁移环境
flask db init

# 生成迁移脚本
flask db migrate -m "描述信息"

# 应用迁移
flask db upgrade
```

## 8. 性能优化建议

1. **查询优化**：
   - 使用 SQLAlchemy 的懒加载和关联预加载优化查询
   - 避免 N+1 查询问题
   - 对频繁查询的字段添加适当索引

2. **分页查询**：
   - 日记列表查询使用分页，避免一次性加载过多数据
   - 推荐每页显示 10-20 条记录

3. **缓存策略**：
   - 考虑使用 Redis 缓存热点数据，如用户会话信息
   - 日记内容可考虑缓存最近访问的记录

## 9. 备份与恢复策略

1. **定期备份**：
   - 每日全量备份
   - 每周增量备份

2. **备份存储**：
   - 备份文件存储在独立的存储系统
   - 至少保留 30 天的备份

3. **恢复测试**：
   - 每月进行一次恢复测试，确保备份有效

## 10. 未来扩展考虑

1. **数据分片**：
   - 随着用户和日记数量增长，考虑按用户ID进行水平分片

2. **读写分离**：
   - 主库负责写操作，从库负责读操作，提高并发性能

3. **全文搜索**：
   - 考虑集成 Elasticsearch 实现日记内容的全文搜索功能