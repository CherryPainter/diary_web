# API 文档

## 1. API 概述

本文档描述了日记Web应用的RESTful API接口，包括用户认证、日记管理等功能。所有API接口遵循RESTful设计原则，使用JSON格式进行数据交换。

## 2. 认证与授权

### 2.1 JWT 认证

本应用使用 JWT (JSON Web Token) 进行API认证。所有需要认证的请求必须在请求头中包含有效的 JWT token。

```
Authorization: Bearer <your_token_here>
```

## 3. API 端点

### 3.1 用户认证相关

#### 3.1.1 用户注册

**请求**：
- 方法：`POST`
- 路径：`/api/auth/register`
- 内容类型：`application/json`

**请求体**：
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "question": "string",
  "answer": "string"
}
```

**响应**：
- 成功 (201 Created)：
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2025-10-24T12:00:00Z"
  }
  ```
- 失败 (400 Bad Request)：
  ```json
  {
    "message": "注册失败",
    "errors": {
      "username": "用户名已存在",
      "email": "邮箱格式不正确"
    }
  }
  ```

#### 3.1.2 用户登录

**请求**：
- 方法：`POST`
- 路径：`/api/auth/login`
- 内容类型：`application/json`

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "token": "jwt_token_string",
    "user": {
      "id": 1,
      "username": "string",
      "email": "string"
    }
  }
  ```
- 失败 (401 Unauthorized)：
  ```json
  {
    "message": "用户名或密码错误"
  }
  ```
- 失败 (423 Locked)：
  ```json
  {
    "message": "账户已被锁定，请稍后再试",
    "locked_until": "2025-10-24T13:00:00Z"
  }
  ```

#### 3.1.3 用户登出

**请求**：
- 方法：`POST`
- 路径：`/api/auth/logout`
- 头部：`Authorization: Bearer <token>`

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "message": "登出成功"
  }
  ```

#### 3.1.4 密码重置请求

**请求**：
- 方法：`POST`
- 路径：`/api/auth/reset-request`
- 内容类型：`application/json`

**请求体**：
```json
{
  "username": "string",
  "question": "string",
  "answer": "string"
}
```

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "message": "验证成功，请设置新密码"
  }
  ```
- 失败 (400 Bad Request)：
  ```json
  {
    "message": "验证失败"
  }
  ```

#### 3.1.5 重置密码

**请求**：
- 方法：`POST`
- 路径：`/api/auth/reset-password`
- 内容类型：`application/json`

**请求体**：
```json
{
  "username": "string",
  "new_password": "string"
}
```

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "message": "密码重置成功"
  }
  ```
- 失败 (400 Bad Request)：
  ```json
  {
    "message": "密码重置失败"
  }
  ```

### 3.2 日记管理相关

#### 3.2.1 获取日记列表

**请求**：
- 方法：`GET`
- 路径：`/api/diaries?page=1&per_page=10`
- 头部：`Authorization: Bearer <token>`

**查询参数**：
- `page`：页码（默认1）
- `per_page`：每页数量（默认10，最大100）
- `sort`：排序字段（默认created_at）
- `order`：排序方向（asc或desc，默认desc）

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "items": [
      {
        "id": 1,
        "title": "string",
        "content": "string",
        "created_at": "2025-10-24T12:00:00Z",
        "updated_at": "2025-10-24T12:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "per_page": 10,
    "pages": 10
  }
  ```

#### 3.2.2 获取单篇日记

**请求**：
- 方法：`GET`
- 路径：`/api/diaries/{diary_id}`
- 头部：`Authorization: Bearer <token>`

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "id": 1,
    "title": "string",
    "content": "string",
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:00:00Z"
  }
  ```
- 失败 (404 Not Found)：
  ```json
  {
    "message": "日记不存在"
  }
  ```

#### 3.2.3 创建日记

**请求**：
- 方法：`POST`
- 路径：`/api/diaries`
- 头部：`Authorization: Bearer <token>`
- 内容类型：`application/json`

**请求体**：
```json
{
  "title": "string",
  "content": "string"
}
```

**响应**：
- 成功 (201 Created)：
  ```json
  {
    "id": 1,
    "title": "string",
    "content": "string",
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:00:00Z"
  }
  ```
- 失败 (400 Bad Request)：
  ```json
  {
    "message": "创建失败",
    "errors": {
      "title": "标题不能为空",
      "content": "内容不能为空"
    }
  }
  ```

#### 3.2.4 更新日记

**请求**：
- 方法：`PUT`
- 路径：`/api/diaries/{diary_id}`
- 头部：`Authorization: Bearer <token>`
- 内容类型：`application/json`

**请求体**：
```json
{
  "title": "string",
  "content": "string"
}
```

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "id": 1,
    "title": "string",
    "content": "string",
    "created_at": "2025-10-24T12:00:00Z",
    "updated_at": "2025-10-24T12:30:00Z"
  }
  ```
- 失败 (404 Not Found)：
  ```json
  {
    "message": "日记不存在"
  }
  ```
- 失败 (403 Forbidden)：
  ```json
  {
    "message": "无权修改此日记"
  }
  ```

#### 3.2.5 删除日记

**请求**：
- 方法：`DELETE`
- 路径：`/api/diaries/{diary_id}`
- 头部：`Authorization: Bearer <token>`

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "message": "删除成功"
  }
  ```
- 失败 (404 Not Found)：
  ```json
  {
    "message": "日记不存在"
  }
  ```
- 失败 (403 Forbidden)：
  ```json
  {
    "message": "无权删除此日记"
  }
  ```

### 3.3 用户信息相关

#### 3.3.1 获取当前用户信息

**请求**：
- 方法：`GET`
- 路径：`/api/users/me`
- 头部：`Authorization: Bearer <token>`

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2025-10-24T12:00:00Z"
  }
  ```

#### 3.3.2 更新用户信息

**请求**：
- 方法：`PUT`
- 路径：`/api/users/me`
- 头部：`Authorization: Bearer <token>`
- 内容类型：`application/json`

**请求体**：
```json
{
  "email": "string",
  "password": "string"  // 可选，留空表示不修改
}
```

**响应**：
- 成功 (200 OK)：
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2025-10-24T12:00:00Z"
  }
  ```
- 失败 (400 Bad Request)：
  ```json
  {
    "message": "更新失败",
    "errors": {
      "email": "邮箱格式不正确"
    }
  }
  ```

## 4. 错误处理

所有API错误响应都包含以下格式：

```json
{
  "message": "错误描述",
  "errors": {  // 可选，特定字段的错误
    "field_name": "字段错误描述"
  }
}
```

常见的HTTP状态码：
- `200 OK`：请求成功
- `201 Created`：资源创建成功
- `400 Bad Request`：请求参数错误
- `401 Unauthorized`：未授权，需要登录
- `403 Forbidden`：拒绝访问，权限不足
- `404 Not Found`：资源不存在
- `429 Too Many Requests`：请求过于频繁
- `500 Internal Server Error`：服务器内部错误

## 5. 请求限流

API实现了请求限流机制，防止滥用：
- 未认证请求：每分钟最多60次
- 已认证请求：每分钟最多300次
- 特定敏感操作（如登录）：每分钟最多10次

限流响应示例：
```json
{
  "message": "请求过于频繁，请稍后再试",
  "retry_after": 60
}
```

## 6. API 版本控制

当前API版本为 v1，通过URL路径 `/api/v1/` 访问。未来可能会推出新的API版本，旧版本将在一段时间内保持兼容。

## 7. 示例代码

### 7.1 Python (使用 requests)

```python
import requests

# 登录获取token
def login(username, password):
    url = "http://localhost:5000/api/auth/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception(f"登录失败: {response.json()['message']}")

# 获取日记列表
def get_diaries(token):
    url = "http://localhost:5000/api/diaries"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# 创建日记
def create_diary(token, title, content):
    url = "http://localhost:5000/api/diaries"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title, "content": content}
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### 7.2 JavaScript (使用 fetch)

```javascript
// 登录获取token
async function login(username, password) {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  if (response.ok) {
    return data.token;
  } else {
    throw new Error(data.message);
  }
}

// 获取日记列表
async function getDiaries(token) {
  const response = await fetch('http://localhost:5000/api/diaries', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
}

// 创建日记
async function createDiary(token, title, content) {
  const response = await fetch('http://localhost:5000/api/diaries', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ title, content })
  });
  return response.json();
}
```