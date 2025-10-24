# 代码规范文档

本文档定义了日记Web应用项目的代码规范，所有贡献者都应遵循这些规范，以确保代码的一致性、可读性和可维护性。

## 1. Python 代码规范

### 1.1 基本规范

- **遵循 PEP 8**：本项目严格遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 编码规范
- **缩进**：使用 4 个空格进行缩进，不使用制表符 (Tab)
- **行长度**：每行代码不超过 79 个字符
- **空行**：
  - 顶级函数和类定义之间使用两个空行
  - 类内部的方法定义之间使用一个空行
  - 函数内部逻辑分段时使用一个空行

### 1.2 命名规范

- **类名**：使用驼峰命名法 (CamelCase)，如 `UserManager`
- **函数和方法名**：使用下划线分隔的小写命名法 (snake_case)，如 `get_user_by_id`
- **变量名**：使用下划线分隔的小写命名法 (snake_case)，如 `user_count`
- **常量名**：使用全大写字母和下划线分隔，如 `MAX_RETRY_COUNT`
- **模块名**：使用短的、全小写的名称，避免使用下划线，如 `auth`
- **包名**：使用短的、全小写的名称，避免使用下划线，如 `diary_app`

### 1.3 导入规范

- 导入应按照以下顺序分组：
  1. 标准库导入
  2. 第三方库导入
  3. 本地应用导入
- 每组导入之间使用一个空行分隔
- 使用绝对导入，避免使用相对导入
- 避免使用 `from module import *` 导入方式

```python
# 标准库导入
import os
import datetime

# 第三方库导入
from flask import Flask, render_template
from sqlalchemy import Column, Integer, String

# 本地应用导入
from diary_app.extensions import db
from diary_app.models import User
```

### 1.4 类型提示

- 使用 Python 的类型提示系统提供类型信息
- 为所有函数参数和返回值添加类型注解
- 使用标准库中的 `typing` 模块定义复杂类型

```python
from typing import List, Optional, Dict, Any

def get_users(limit: int = 100) -> List[User]:
    """获取用户列表"""
    pass

def get_user_by_id(user_id: int) -> Optional[User]:
    """通过ID获取用户"""
    pass
```

### 1.5 文档字符串

- 使用 Google 风格的文档字符串
- 为所有公共函数、类和模块添加文档字符串
- 文档字符串应包括函数功能、参数说明、返回值说明和异常说明

```python
def authenticate_user(username: str, password: str) -> Optional[User]:
    """验证用户身份

    Args:
        username: 用户名
        password: 密码

    Returns:
        验证成功返回用户对象，失败返回None

    Raises:
        ValueError: 当输入参数无效时
    """
    pass
```

### 1.6 注释

- 使用注释解释复杂的逻辑和算法
- 避免不必要的注释，代码本身应该具有自解释性
- 行注释使用 `#` 后跟一个空格开始
- 块注释每行以 `#` 开始，行与行之间对齐

```python
# 这是一个行注释

# 这是一个块注释的第一行
# 这是块注释的第二行
# 解释一个复杂的算法或业务逻辑
```

### 1.7 异常处理

- 使用具体的异常类型，避免使用通用的 `Exception`
- 异常消息应清晰描述错误原因
- 异常处理应具有针对性，不要捕获所有异常

```python
# 推荐做法
try:
    db.session.commit()
except IntegrityError as e:
    db.session.rollback()
    raise ValueError(f"数据库完整性错误: {str(e)}")
```

## 2. HTML/CSS 代码规范

### 2.1 HTML 规范

- 使用语义化标签，如 `<header>`, `<nav>`, `<main>`, `<article>`, `<footer>`
- 缩进使用 2 个空格
- 标签和属性名使用小写
- 所有属性值必须使用双引号
- 自闭合标签必须包含斜杠，如 `<img src="..." />`
- 避免内联样式和内联脚本

```html
<!-- 推荐做法 -->
<section class="diary-container">
  <article class="diary-entry">
    <h2>日记标题</h2>
    <p>日记内容</p>
    <time datetime="2025-10-24">2025年10月24日</time>
  </article>
</section>
```

### 2.2 CSS 规范

- 使用 2 个空格进行缩进
- 选择器名称使用小写字母和短横线分隔
- 属性名和冒号之间不留空格，冒号和值之间留一个空格
- 每条样式规则结束后必须加分号
- 多个选择器使用相同样式时，每个选择器单独占一行
- 样式声明使用大括号包裹，左大括号与选择器在同一行

```css
/* 推荐做法 */
.diary-entry {
  background-color: #ffffff;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.diary-entry h2,
.diary-entry p {
  margin: 0 0 12px 0;
}
```

### 2.3 CSS 命名规范

- 使用 BEM (Block Element Modifier) 命名约定
- 块名使用短横线分隔，如 `.diary-container`
- 元素使用双下划线连接，如 `.diary-container__entry`
- 修饰符使用双短横线连接，如 `.diary-entry--featured`

## 3. JavaScript 代码规范

### 3.1 基本规范

- 使用 2 个空格进行缩进
- 行长度不超过 80 个字符
- 语句结束后必须加分号
- 使用单引号定义字符串，除非字符串中包含单引号需要转义
- 大括号风格：左大括号与语句在同一行，右大括号单独占一行

```javascript
// 推荐做法
function validateForm() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  if (!username || !password) {
    alert('请输入用户名和密码');
    return false;
  }
  
  return true;
}
```

### 3.2 命名规范

- **变量和函数名**：使用小驼峰命名法 (camelCase)，如 `getUserData`
- **类名**：使用大驼峰命名法 (PascalCase)，如 `UserService`
- **常量**：使用全大写字母和下划线分隔，如 `MAX_RETRIES`
- **私有变量/方法**：前缀使用下划线，如 `_privateMethod`

### 3.3 现代 JavaScript 特性

- 使用 `const` 和 `let` 代替 `var`
- 优先使用箭头函数
- 使用模板字符串进行字符串拼接
- 使用解构赋值简化代码
- 使用 Promise 和 async/await 处理异步操作

```javascript
// 推荐做法
const fetchUser = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('获取用户数据失败:', error);
    throw error;
  }
};
```

### 3.4 注释规范

- 单行注释使用 `//`
- 多行注释使用 `/* */`
- 为函数、类和复杂逻辑添加 JSDoc 风格注释

```javascript
/**
 * 验证用户输入
 * @param {string} username - 用户名
 * @param {string} password - 密码
 * @returns {boolean} 验证是否通过
 */
function validateInput(username, password) {
  // 检查用户名和密码是否为空
  if (!username || !password) {
    return false;
  }
  
  /*
   * 检查密码复杂度：
   * 1. 长度至少8位
   * 2. 包含大小写字母
   * 3. 包含数字
   */
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  return passwordRegex.test(password);
}
```

## 4. 数据库交互规范

### 4.1 SQLAlchemy 使用规范

- 使用 SQLAlchemy 的 ORM 方式操作数据库，避免直接执行 SQL 语句
- 使用上下文管理器 `with` 处理数据库会话
- 数据库操作应使用事务，并在失败时回滚
- 查询结果使用分页，避免一次性加载大量数据

```python
# 推荐做法
from sqlalchemy import desc
from diary_app.extensions import db
from diary_app.models import DiaryEntry

def get_user_diaries(user_id, page=1, per_page=10):
    """获取用户的日记列表（分页）"""
    return DiaryEntry.query.filter_by(user_id=user_id)\
        .order_by(desc(DiaryEntry.created_at))\
        .paginate(page=page, per_page=per_page, error_out=False)

def create_diary(user_id, title, content):
    """创建新日记"""
    diary = DiaryEntry(
        user_id=user_id,
        title=title,
        content=content
    )
    
    try:
        db.session.add(diary)
        db.session.commit()
        return diary
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"创建日记失败: {str(e)}")
```

### 4.2 模型定义规范

- 模型类使用驼峰命名法
- 表名使用小写和下划线分隔
- 字段名使用小写和下划线分隔
- 外键命名格式为 `关联表名_id`
- 为模型添加适当的索引

## 5. 安全规范

### 5.1 密码安全

- 密码必须使用 Werkzeug 的 `generate_password_hash` 函数进行哈希处理
- 验证密码使用 `check_password_hash` 函数
- 永远不要在日志中打印密码或敏感信息

```python
# 推荐做法
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(password):
    self.password_hash = generate_password_hash(password)

def verify_password(password):
    return check_password_hash(self.password_hash, password)
```

### 5.2 SQL 注入防护

- 使用参数化查询或 ORM，避免字符串拼接构建 SQL
- 对用户输入进行验证和清洗
- 限制数据库用户权限，遵循最小权限原则

### 5.3 XSS 防护

- 对所有用户输入进行 HTML 转义
- 使用 Jinja2 模板时默认启用自动转义
- 使用 `safe` 过滤器时要确保内容已经过安全验证

## 6. 测试规范

### 6.1 测试文件组织

- 测试文件放在 `tests` 目录下
- 测试文件名格式为 `test_模块名.py`
- 测试函数名格式为 `test_函数名`

### 6.2 测试内容

- 单元测试应测试最小的可测试单元（函数、方法）
- 每个测试应该只测试一个断言
- 测试应包含正常流程和异常流程
- 测试应独立运行，不依赖于其他测试的结果

```python
import unittest
from diary_app.models import User
from diary_app.extensions import db

class UserModelTestCase(unittest.TestCase):
    def test_password_setting(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        self.assertTrue(user.password_hash is not None)
    
    def test_password_verification(self):
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
```

## 7. 提交规范

### 7.1 提交消息格式

提交消息应遵循以下格式：

```
<类型>: <简短描述>

<详细说明>（如果需要）

<相关issue或PR链接>（如果有）
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更改
- `style`: 代码风格更改（不影响功能）
- `refactor`: 代码重构（不添加功能，不修复bug）
- `test`: 测试相关更改
- `chore`: 构建过程或辅助工具的更改

### 7.2 提交频率

- 每个提交应该包含一个逻辑上的更改
- 避免一次性提交大量不相关的更改
- 频繁提交小的更改，而不是很少提交大的更改

## 8. 代码审查规范

### 8.1 审查流程

- 所有代码必须经过至少一次审查才能合并到主分支
- 审查者应检查代码是否符合项目规范
- 审查者应检查代码的逻辑正确性和潜在问题
- 审查者应提供建设性的反馈

### 8.2 审查标准

- 代码是否符合本文档定义的规范
- 代码是否有清晰的文档和注释
- 代码是否处理了边缘情况和错误
- 代码是否有性能问题或安全隐患

## 9. 持续集成规范

- 所有代码提交必须通过 CI/CD 管道的检查
- CI 管道应包括代码风格检查、单元测试、安全扫描等
- 只有通过所有检查的代码才能合并到主分支

## 10. 工具推荐

### 10.1 Python 工具

- **代码格式化**: Black, isort
- **代码检查**: Pylint, Flake8
- **类型检查**: Mypy
- **测试框架**: pytest

### 10.2 JavaScript 工具

- **代码格式化**: Prettier
- **代码检查**: ESLint
- **测试框架**: Jest

### 10.3 编辑器配置

推荐使用 EditorConfig 保持跨编辑器的一致配置：

```editorconfig
# EditorConfig 配置
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{js,html,css}]
indent_size = 2

[*.py]
indent_size = 4
```

## 11. 最佳实践

- **KISS 原则**: 保持简单，避免过度设计
- **DRY 原则**: 不要重复自己，提取共用代码
- **YAGNI 原则**: 除非必要，不要添加功能
- **最小惊讶原则**: 代码行为应符合预期，避免意外结果
- **错误处理**: 总是处理可能的错误情况
- **日志记录**: 记录重要的操作和错误信息
- **性能考虑**: 避免不必要的计算和数据库查询
- **安全优先**: 始终考虑潜在的安全问题

---

本规范文档将随项目发展不断更新和完善，请确保使用最新版本的规范。如有任何疑问或建议，请通过项目的问题追踪系统提出。