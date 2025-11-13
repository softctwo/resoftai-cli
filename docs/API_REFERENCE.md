# ResoftAI API 参考文档

## 概述

ResoftAI 提供完整的 RESTful API，支持多智能体协作软件开发。所有 API 端点都需要 JWT 认证。

### 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **文档**: http://localhost:8000/docs

### 响应格式

所有 API 响应都遵循标准格式：

```json
{
  "data": {},
  "message": "操作成功",
  "success": true
}
```

错误响应：

```json
{
  "detail": "错误描述",
  "error": "错误类型",
  "status_code": 400
}
```

## 认证 API

### 用户注册

注册新用户账户。

**端点**: `POST /api/auth/register`

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "user",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "用户注册成功",
  "success": true
}
```

### 用户登录

用户登录获取访问令牌。

**端点**: `POST /api/auth/login`

**请求体** (表单数据):
```
username=admin&password=admin123
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 获取当前用户

获取当前登录用户信息。

**端点**: `GET /api/auth/me`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@resoftai.com",
    "full_name": "Administrator",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "获取用户信息成功",
  "success": true
}
```

### 刷新令牌

使用刷新令牌获取新的访问令牌。

**端点**: `POST /api/auth/refresh`

**Headers**:
```
Authorization: Bearer <refresh_token>
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 用户登出

用户登出系统。

**端点**: `POST /api/auth/logout`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "用户登出成功",
  "success": true
}
```

## 项目管理 API

### 获取项目列表

获取用户的所有项目。

**端点**: `GET /api/projects`

**Headers**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page` (int): 页码，默认 1
- `size` (int): 每页大小，默认 20
- `status` (string): 项目状态过滤

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "任务管理系统",
      "description": "现代化的任务管理 Web 应用",
      "status": "completed",
      "progress": 100,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T02:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 1,
    "pages": 1
  },
  "message": "获取项目列表成功",
  "success": true
}
```

### 创建项目

创建新项目。

**端点**: `POST /api/projects`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "项目名称",
  "description": "项目描述",
  "requirements": "项目需求描述"
}
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "项目名称",
    "description": "项目描述",
    "requirements": "项目需求描述",
    "status": "pending",
    "progress": 0,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "项目创建成功",
  "success": true
}
```

### 获取项目详情

获取指定项目的详细信息。

**端点**: `GET /api/projects/{project_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "任务管理系统",
    "description": "现代化的任务管理 Web 应用",
    "requirements": "开发一个支持用户注册、任务创建、分配和追踪的 Web 应用",
    "status": "completed",
    "progress": 100,
    "current_stage": "completed",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T02:00:00",
    "files": [
      {
        "id": 1,
        "name": "requirements.md",
        "path": "/docs/requirements.md",
        "type": "markdown",
        "size": 2048
      }
    ]
  },
  "message": "获取项目详情成功",
  "success": true
}
```

### 更新项目

更新项目信息。

**端点**: `PUT /api/projects/{project_id}`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "更新后的项目名称",
  "description": "更新后的项目描述",
  "requirements": "更新后的项目需求"
}
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "更新后的项目名称",
    "description": "更新后的项目描述",
    "requirements": "更新后的项目需求",
    "status": "pending",
    "progress": 0,
    "updated_at": "2024-01-01T01:00:00"
  },
  "message": "项目更新成功",
  "success": true
}
```

### 删除项目

删除指定项目。

**端点**: `DELETE /api/projects/{project_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "项目删除成功",
  "success": true
}
```