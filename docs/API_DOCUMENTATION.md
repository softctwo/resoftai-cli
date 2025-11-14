# ResoftAI API 文档

**版本**: v0.2.2
**Base URL**: `http://localhost:8000/api`
**文档最后更新**: 2025-11-14

---

## 目录

1. [概述](#概述)
2. [认证](#认证)
3. [错误处理](#错误处理)
4. [限流](#限流)
5. [认证端点](#认证端点)
6. [项目管理](#项目管理)
7. [文件管理](#文件管理)
8. [LLM配置](#llm配置)
9. [智能体活动](#智能体活动)
10. [模板系统](#模板系统)
11. [代码质量](#代码质量)
12. [插件系统](#插件系统)
13. [企业版API](#企业版api)
14. [性能监控](#性能监控)
15. [WebSocket](#websocket)

---

## 概述

### API 特性

- **RESTful 设计**: 遵循 REST 架构风格
- **JSON 格式**: 所有请求和响应使用 JSON
- **JWT 认证**: Bearer Token 认证机制
- **异步处理**: 高性能异步 API
- **OpenAPI 文档**: 访问 `/docs` 查看交互式文档
- **版本控制**: API 版本在 URL 路径中（未来支持）

### HTTP 方法

- **GET**: 获取资源
- **POST**: 创建资源
- **PUT**: 更新整个资源
- **PATCH**: 部分更新资源
- **DELETE**: 删除资源

### 数据格式

所有请求和响应使用 JSON 格式：

```
Content-Type: application/json
Accept: application/json
```

### 日期时间格式

使用 ISO 8601 格式：

```
2025-11-14T10:30:00Z
```

---

## 认证

### JWT Token 认证

大多数 API 需要 JWT Token 认证。在请求头中包含 Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token 类型

#### Access Token
- **用途**: API 访问
- **有效期**: 30分钟
- **刷新**: 使用 Refresh Token

#### Refresh Token
- **用途**: 刷新 Access Token
- **有效期**: 7天
- **存储**: 安全存储，不要暴露在客户端

### 获取 Token

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePass123!
```

响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 刷新 Token

```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述",
  "status_code": 400,
  "error_code": "INVALID_REQUEST",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

### HTTP 状态码

| 状态码 | 说明 | 常见原因 |
|--------|------|---------|
| 200 | 成功 | 请求成功 |
| 201 | 已创建 | 资源创建成功 |
| 204 | 无内容 | 删除成功 |
| 400 | 请求错误 | 参数验证失败 |
| 401 | 未认证 | Token 无效或过期 |
| 403 | 权限不足 | 无访问权限 |
| 404 | 未找到 | 资源不存在 |
| 409 | 冲突 | 资源已存在 |
| 422 | 验证错误 | 数据验证失败 |
| 429 | 请求过多 | 超过限流阈值 |
| 500 | 服务器错误 | 内部错误 |
| 503 | 服务不可用 | 服务暂时不可用 |

### 验证错误详情

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 限流

### 限流规则

- **免费用户**: 60 请求/分钟
- **付费用户**: 300 请求/分钟
- **企业用户**: 1000 请求/分钟

### 限流响应头

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1699960800
```

### 超过限流

```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "status_code": 429
}
```

---

## 认证端点

### 注册用户

创建新用户账户。

```http
POST /api/auth/register
Content-Type: application/json
```

**请求体**:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**响应** (201):

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-14T10:00:00Z"
}
```

**错误**:

- `400`: 用户名或邮箱已存在
- `422`: 密码强度不足

### 登录

获取 JWT Token。

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded
```

**请求体**:

```
username=john@example.com&password=SecurePass123!
```

**响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**错误**:

- `401`: 用户名或密码错误
- `403`: 账户已被禁用

### 刷新 Token

使用 Refresh Token 获取新的 Access Token。

```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**响应** (200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 获取当前用户

获取当前登录用户信息。

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-11-14T10:00:00Z"
}
```

### 更新用户信息

更新当前用户的信息。

```http
PUT /api/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

**响应** (200):

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john.smith@example.com",
  "full_name": "John Smith",
  "is_active": true,
  "is_admin": false,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 修改密码

修改当前用户的密码。

```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "current_password": "OldPass123!",
  "new_password": "NewSecurePass123!"
}
```

**响应** (200):

```json
{
  "message": "Password changed successfully"
}
```

**错误**:

- `401`: 当前密码错误
- `422`: 新密码不符合安全要求

---

## 项目管理

### 创建项目

创建新的开发项目。

```http
POST /api/projects
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "name": "我的Web应用",
  "description": "一个现代化的Web应用",
  "requirements": "开发一个用户管理系统，包括注册、登录、权限控制等功能。使用FastAPI和React。",
  "config": {
    "execution_strategy": "adaptive",
    "enable_cache": true,
    "enable_checkpoints": true,
    "parallel_stages": ["architecture_design", "ui_design"]
  }
}
```

**参数说明**:

- `name` (必需): 项目名称
- `description`: 项目描述
- `requirements` (必需): 详细需求说明
- `config`: 工作流配置
  - `execution_strategy`: 执行策略 (`sequential`, `parallel`, `adaptive`)
  - `enable_cache`: 是否启用缓存
  - `enable_checkpoints`: 是否启用检查点
  - `parallel_stages`: 可并行执行的阶段

**响应** (201):

```json
{
  "id": 1,
  "user_id": 1,
  "name": "我的Web应用",
  "description": "一个现代化的Web应用",
  "requirements": "开发一个用户管理系统...",
  "status": "pending",
  "progress": 0,
  "current_stage": null,
  "config": {...},
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

**错误**:

- `400`: 参数验证失败
- `401`: 未认证
- `403`: 配额已满

### 获取项目列表

获取当前用户的所有项目。

```http
GET /api/projects?skip=0&limit=20&status=completed
Authorization: Bearer <access_token>
```

**查询参数**:

- `skip`: 跳过的记录数（分页）
- `limit`: 返回的记录数（最大100）
- `status`: 按状态筛选 (`pending`, `running`, `completed`, `failed`, `cancelled`)

**响应** (200):

```json
[
  {
    "id": 1,
    "name": "我的Web应用",
    "description": "一个现代化的Web应用",
    "status": "completed",
    "progress": 100,
    "current_stage": "completion",
    "created_at": "2025-11-14T10:00:00Z",
    "updated_at": "2025-11-14T10:30:00Z",
    "completed_at": "2025-11-14T10:30:00Z"
  }
]
```

### 获取项目详情

获取指定项目的详细信息。

```http
GET /api/projects/{project_id}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "user_id": 1,
  "name": "我的Web应用",
  "description": "一个现代化的Web应用",
  "requirements": "开发一个用户管理系统...",
  "status": "completed",
  "progress": 100,
  "current_stage": "completion",
  "config": {...},
  "deliverables": {
    "srs_document": "...",
    "architecture_design": "...",
    "code_files": [...]
  },
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:30:00Z",
  "completed_at": "2025-11-14T10:30:00Z"
}
```

**错误**:

- `404`: 项目不存在
- `403`: 无访问权限

### 更新项目

更新项目信息。

```http
PUT /api/projects/{project_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "name": "更新的项目名称",
  "description": "更新的描述",
  "requirements": "更新的需求"
}
```

**响应** (200):

```json
{
  "id": 1,
  "name": "更新的项目名称",
  "description": "更新的描述",
  "requirements": "更新的需求",
  "updated_at": "2025-11-14T11:00:00Z"
}
```

**注意**: 只能更新状态为 `pending` 的项目。

### 删除项目

删除指定项目及其所有相关数据。

```http
DELETE /api/projects/{project_id}
Authorization: Bearer <access_token>
```

**响应** (204):

无响应体。

**错误**:

- `404`: 项目不存在
- `403`: 无删除权限

### 启动工作流

启动项目的工作流执行。

```http
POST /api/projects/{project_id}/execute
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "project_id": 1,
  "workflow_id": "wf_1699960800_abc123",
  "status": "running",
  "current_stage": "requirements_analysis",
  "started_at": "2025-11-14T10:00:00Z"
}
```

**错误**:

- `400`: 项目已在运行
- `404`: 项目不存在
- `422`: 项目配置无效

### 停止工作流

停止正在运行的工作流。

```http
POST /api/projects/{project_id}/stop
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "project_id": 1,
  "status": "cancelled",
  "stopped_at": "2025-11-14T10:15:00Z"
}
```

### 从检查点恢复

从上次保存的检查点恢复工作流执行。

```http
POST /api/projects/{project_id}/resume
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "project_id": 1,
  "workflow_id": "wf_1699960800_abc123",
  "status": "running",
  "current_stage": "development",
  "resumed_at": "2025-11-14T10:20:00Z",
  "checkpoint_stage": "ui_design"
}
```

### 下载项目

下载项目的所有交付物。

```http
GET /api/projects/{project_id}/download
Authorization: Bearer <access_token>
```

**响应** (200):

```
Content-Type: application/zip
Content-Disposition: attachment; filename="project_1.zip"

[二进制ZIP文件]
```

---

## 文件管理

### 上传文件

上传文件到项目。

```http
POST /api/files
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**表单数据**:

```
file: <binary>
project_id: 1
category: requirements  # 可选: requirements, design, code, test, documentation
```

**响应** (201):

```json
{
  "id": 1,
  "project_id": 1,
  "filename": "requirements.txt",
  "category": "requirements",
  "size": 1024,
  "mime_type": "text/plain",
  "version": 1,
  "created_at": "2025-11-14T10:00:00Z"
}
```

**错误**:

- `400`: 文件过大或类型不支持
- `404`: 项目不存在
- `413`: 文件超过最大限制

### 获取文件列表

获取项目的所有文件。

```http
GET /api/files?project_id=1&category=code
Authorization: Bearer <access_token>
```

**查询参数**:

- `project_id` (必需): 项目ID
- `category`: 按分类筛选
- `skip`: 跳过的记录数
- `limit`: 返回的记录数

**响应** (200):

```json
[
  {
    "id": 1,
    "project_id": 1,
    "filename": "main.py",
    "category": "code",
    "size": 2048,
    "version": 2,
    "created_at": "2025-11-14T10:00:00Z",
    "updated_at": "2025-11-14T10:15:00Z"
  }
]
```

### 获取文件详情

获取文件的详细信息和内容。

```http
GET /api/files/{file_id}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "project_id": 1,
  "filename": "main.py",
  "category": "code",
  "size": 2048,
  "mime_type": "text/x-python",
  "content": "# Python code here...",
  "version": 2,
  "created_by": 1,
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:15:00Z"
}
```

### 下载文件

下载文件内容。

```http
GET /api/files/{file_id}/download
Authorization: Bearer <access_token>
```

**响应** (200):

```
Content-Type: text/x-python
Content-Disposition: attachment; filename="main.py"

# Python code here...
```

### 更新文件

更新文件内容（创建新版本）。

```http
PUT /api/files/{file_id}
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**表单数据**:

```
file: <binary>
```

**响应** (200):

```json
{
  "id": 1,
  "project_id": 1,
  "filename": "main.py",
  "size": 2560,
  "version": 3,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 删除文件

删除文件及其所有版本。

```http
DELETE /api/files/{file_id}
Authorization: Bearer <access_token>
```

**响应** (204):

无响应体。

### 获取文件版本历史

获取文件的所有历史版本。

```http
GET /api/files/{file_id}/versions
Authorization: Bearer <access_token>
```

**响应** (200):

```json
[
  {
    "version": 3,
    "size": 2560,
    "created_at": "2025-11-14T10:30:00Z",
    "created_by": 1
  },
  {
    "version": 2,
    "size": 2048,
    "created_at": "2025-11-14T10:15:00Z",
    "created_by": 1
  },
  {
    "version": 1,
    "size": 1536,
    "created_at": "2025-11-14T10:00:00Z",
    "created_by": 1
  }
]
```

### 恢复文件版本

恢复到指定版本。

```http
POST /api/files/{file_id}/versions/{version}/restore
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "filename": "main.py",
  "version": 4,
  "restored_from_version": 2,
  "updated_at": "2025-11-14T10:45:00Z"
}
```

---

## LLM配置

### 创建LLM配置

添加新的LLM提供商配置。

```http
POST /api/llm-configs
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "name": "我的DeepSeek配置",
  "provider": "deepseek",
  "model": "deepseek-chat",
  "api_key": "sk-xxxxxxxxxxxxx",
  "api_base": "https://api.deepseek.com",
  "is_default": true,
  "config": {
    "temperature": 0.7,
    "max_tokens": 4000,
    "top_p": 0.9
  }
}
```

**参数说明**:

- `name`: 配置名称
- `provider`: 提供商 (`deepseek`, `anthropic`, `google`, `moonshot`, `zhipu`, `minimax`)
- `model`: 模型名称
- `api_key`: API密钥
- `api_base`: API基础URL（可选）
- `is_default`: 是否设为默认
- `config`: 额外配置参数

**响应** (201):

```json
{
  "id": 1,
  "user_id": 1,
  "name": "我的DeepSeek配置",
  "provider": "deepseek",
  "model": "deepseek-chat",
  "is_default": true,
  "is_active": true,
  "created_at": "2025-11-14T10:00:00Z"
}
```

### 获取LLM配置列表

获取当前用户的所有LLM配置。

```http
GET /api/llm-configs
Authorization: Bearer <access_token>
```

**响应** (200):

```json
[
  {
    "id": 1,
    "name": "我的DeepSeek配置",
    "provider": "deepseek",
    "model": "deepseek-chat",
    "is_default": true,
    "is_active": true,
    "created_at": "2025-11-14T10:00:00Z"
  }
]
```

### 更新LLM配置

更新LLM配置信息。

```http
PUT /api/llm-configs/{config_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "name": "更新的配置名称",
  "is_default": true,
  "config": {
    "temperature": 0.8
  }
}
```

**响应** (200):

```json
{
  "id": 1,
  "name": "更新的配置名称",
  "is_default": true,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 测试LLM配置

测试LLM配置是否可用。

```http
POST /api/llm-configs/{config_id}/test
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "success": true,
  "model": "deepseek-chat",
  "response_time_ms": 1250,
  "test_output": "Hello! How can I assist you today?"
}
```

**错误**:

- `400`: 配置无效
- `503`: LLM服务不可用

### 删除LLM配置

删除LLM配置。

```http
DELETE /api/llm-configs/{config_id}
Authorization: Bearer <access_token>
```

**响应** (204):

无响应体。

---

## 智能体活动

### 获取智能体活动日志

获取项目的智能体执行日志。

```http
GET /api/agent-activities?project_id=1
Authorization: Bearer <access_token>
```

**查询参数**:

- `project_id` (必需): 项目ID
- `agent_name`: 按智能体名称筛选
- `skip`: 跳过的记录数
- `limit`: 返回的记录数

**响应** (200):

```json
[
  {
    "id": 1,
    "project_id": 1,
    "agent_name": "RequirementsAnalystAgent",
    "stage": "requirements_analysis",
    "status": "completed",
    "input_data": {...},
    "output_data": {...},
    "execution_time_seconds": 120,
    "tokens_used": 3500,
    "started_at": "2025-11-14T10:00:00Z",
    "completed_at": "2025-11-14T10:02:00Z"
  }
]
```

### 获取单个活动详情

获取智能体活动的详细信息。

```http
GET /api/agent-activities/{activity_id}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "project_id": 1,
  "agent_name": "RequirementsAnalystAgent",
  "stage": "requirements_analysis",
  "status": "completed",
  "input_data": {
    "requirements": "开发一个用户管理系统..."
  },
  "output_data": {
    "srs_document": "软件需求规格说明书内容...",
    "use_cases": [...]
  },
  "execution_time_seconds": 120,
  "tokens_used": 3500,
  "error_message": null,
  "started_at": "2025-11-14T10:00:00Z",
  "completed_at": "2025-11-14T10:02:00Z"
}
```

---

## 模板系统

### 获取模板列表

获取所有可用的项目模板。

```http
GET /api/templates?category=backend
Authorization: Bearer <access_token>
```

**查询参数**:

- `category`: 按分类筛选 (`backend`, `frontend`, `fullstack`, `cli`, `mobile`)

**响应** (200):

```json
[
  {
    "id": 1,
    "name": "FastAPI REST API",
    "description": "完整的FastAPI REST API模板",
    "category": "backend",
    "version": "1.0.0",
    "variables": {
      "project_name": {
        "type": "string",
        "description": "项目名称",
        "required": true
      }
    },
    "created_at": "2025-11-01T00:00:00Z"
  }
]
```

### 获取模板详情

获取模板的详细信息。

```http
GET /api/templates/{template_id}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "name": "FastAPI REST API",
  "description": "完整的FastAPI REST API模板",
  "category": "backend",
  "version": "1.0.0",
  "variables": {...},
  "files": [
    "main.py",
    "requirements.txt",
    "README.md",
    "Dockerfile"
  ],
  "preview": "模板预览内容...",
  "created_at": "2025-11-01T00:00:00Z"
}
```

### 应用模板

将模板应用到项目。

```http
POST /api/templates/{template_id}/apply
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "project_id": 1,
  "variables": {
    "project_name": "my-api",
    "database": "postgresql",
    "enable_auth": true
  }
}
```

**响应** (200):

```json
{
  "project_id": 1,
  "template_id": 1,
  "applied_at": "2025-11-14T10:00:00Z",
  "generated_files": [
    "main.py",
    "requirements.txt",
    "README.md"
  ]
}
```

---

## 代码质量

### 分析代码质量

对代码进行质量分析。

```http
POST /api/code-analysis
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "code": "def hello():\n    print('hello')\n",
  "language": "python",
  "file_path": "main.py"
}
```

**响应** (200):

```json
{
  "score": 85,
  "language": "python",
  "issues": [
    {
      "severity": "warning",
      "category": "best_practices",
      "message": "函数缺少文档字符串",
      "line": 1,
      "column": 1
    }
  ],
  "metrics": {
    "lines_of_code": 2,
    "complexity": 1,
    "maintainability_index": 85
  },
  "suggestions": [
    "添加函数文档字符串",
    "考虑使用类型提示"
  ]
}
```

### 批量分析项目代码

分析整个项目的代码质量。

```http
POST /api/code-analysis/project/{project_id}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "project_id": 1,
  "overall_score": 82,
  "total_files": 15,
  "total_lines": 2500,
  "files": [
    {
      "file_path": "main.py",
      "score": 85,
      "issues_count": 3
    }
  ],
  "summary": {
    "critical": 0,
    "high": 2,
    "medium": 8,
    "low": 15
  },
  "analyzed_at": "2025-11-14T10:00:00Z"
}
```

---

## 插件系统

### 获取插件列表

获取插件市场中的所有插件。

```http
GET /api/marketplace/plugins?category=development&sort=popularity
Authorization: Bearer <access_token>
```

**查询参数**:

- `category`: 按分类筛选
- `sort`: 排序方式 (`popularity`, `rating`, `recent`)
- `search`: 搜索关键词
- `skip`: 跳过的记录数
- `limit`: 返回的记录数

**响应** (200):

```json
[
  {
    "slug": "code-formatter",
    "name": "Code Formatter",
    "version": "1.0.0",
    "description": "自动格式化代码",
    "category": "development",
    "author": "ResoftAI Team",
    "rating": 4.5,
    "downloads": 1000,
    "tags": ["formatting", "quality"],
    "created_at": "2025-11-01T00:00:00Z"
  }
]
```

### 获取插件详情

获取插件的详细信息。

```http
GET /api/marketplace/plugins/{slug}
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "slug": "code-formatter",
  "name": "Code Formatter",
  "version": "1.0.0",
  "description": "自动格式化代码",
  "long_description": "详细描述...",
  "category": "development",
  "author": "ResoftAI Team",
  "homepage": "https://example.com",
  "repository": "https://github.com/example/plugin",
  "rating": 4.5,
  "downloads": 1000,
  "tags": ["formatting", "quality"],
  "dependencies": ["black", "isort"],
  "compatibility": {
    "min_version": "0.2.0",
    "max_version": "1.0.0"
  },
  "versions": [
    {"version": "1.0.0", "released_at": "2025-11-01T00:00:00Z"}
  ],
  "reviews": [
    {
      "rating": 5,
      "comment": "非常好用！",
      "author": "user123",
      "created_at": "2025-11-05T10:00:00Z"
    }
  ],
  "created_at": "2025-11-01T00:00:00Z",
  "updated_at": "2025-11-05T00:00:00Z"
}
```

### 安装插件

安装插件到系统。

```http
POST /api/marketplace/plugins/{slug}/install
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "version": "1.0.0",
  "auto_dependencies": true
}
```

**响应** (200):

```json
{
  "slug": "code-formatter",
  "version": "1.0.0",
  "status": "installed",
  "installed_at": "2025-11-14T10:00:00Z"
}
```

**错误**:

- `400`: 插件不兼容
- `409`: 插件已安装

### 获取已安装插件

获取所有已安装的插件。

```http
GET /api/plugins/installed
Authorization: Bearer <access_token>
```

**响应** (200):

```json
[
  {
    "slug": "code-formatter",
    "name": "Code Formatter",
    "version": "1.0.0",
    "is_active": true,
    "installed_at": "2025-11-14T10:00:00Z"
  }
]
```

### 激活/停用插件

切换插件的激活状态。

```http
POST /api/plugins/{slug}/toggle
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "slug": "code-formatter",
  "is_active": false,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 卸载插件

卸载已安装的插件。

```http
DELETE /api/plugins/{slug}
Authorization: Bearer <access_token>
```

**响应** (204):

无响应体。

### 检查插件更新

检查已安装插件的可用更新。

```http
GET /api/marketplace/updates/check
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "updates_available": {
    "code-formatter": {
      "current_version": "1.0.0",
      "latest_version": "1.1.0",
      "changelog": "修复bug，添加新功能"
    }
  }
}
```

### 更新插件

更新插件到最新版本。

```http
POST /api/marketplace/plugins/{slug}/update
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "slug": "code-formatter",
  "old_version": "1.0.0",
  "new_version": "1.1.0",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

### 提交插件评论

为插件添加评论和评分。

```http
POST /api/marketplace/plugins/{slug}/reviews
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "rating": 5,
  "comment": "非常好用的插件！"
}
```

**响应** (201):

```json
{
  "id": 1,
  "plugin_slug": "code-formatter",
  "rating": 5,
  "comment": "非常好用的插件！",
  "author_id": 1,
  "created_at": "2025-11-14T10:00:00Z"
}
```

---

## 企业版API

### 组织管理

#### 创建组织

```http
POST /api/organizations
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "name": "我的公司",
  "slug": "my-company",
  "tier": "professional",
  "contact_email": "admin@company.com",
  "description": "公司描述"
}
```

**响应** (201):

```json
{
  "id": 1,
  "name": "我的公司",
  "slug": "my-company",
  "tier": "professional",
  "is_active": true,
  "sso_enabled": false,
  "created_at": "2025-11-14T10:00:00Z"
}
```

#### 获取组织列表

```http
GET /api/organizations?tier=professional&is_active=true
Authorization: Bearer <access_token>
```

**响应** (200):

```json
[
  {
    "id": 1,
    "name": "我的公司",
    "slug": "my-company",
    "tier": "professional",
    "is_active": true,
    "created_at": "2025-11-14T10:00:00Z"
  }
]
```

#### 更新组织

```http
PUT /api/organizations/{org_id}
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "tier": "enterprise",
  "sso_enabled": true
}
```

**响应** (200):

```json
{
  "id": 1,
  "tier": "enterprise",
  "sso_enabled": true,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 团队管理

#### 创建团队

```http
POST /api/teams
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "organization_id": 1,
  "name": "开发团队",
  "description": "负责核心功能开发",
  "is_default": true
}
```

**响应** (201):

```json
{
  "id": 1,
  "organization_id": 1,
  "name": "开发团队",
  "description": "负责核心功能开发",
  "is_default": true,
  "created_at": "2025-11-14T10:00:00Z"
}
```

#### 添加团队成员

```http
POST /api/teams/{team_id}/members
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "user_id": 10,
  "role": "member"
}
```

**参数说明**:

- `role`: `owner`, `admin`, `member`, `viewer`

**响应** (201):

```json
{
  "id": 1,
  "team_id": 1,
  "user_id": 10,
  "role": "member",
  "joined_at": "2025-11-14T10:00:00Z"
}
```

#### 修改成员角色

```http
PUT /api/teams/{team_id}/members/{user_id}/role
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "role": "admin"
}
```

**响应** (200):

```json
{
  "id": 1,
  "user_id": 10,
  "role": "admin",
  "updated_at": "2025-11-14T10:30:00Z"
}
```

#### 移除团队成员

```http
DELETE /api/teams/{team_id}/members/{user_id}
Authorization: Bearer <access_token>
```

**响应** (204):

无响应体。

### 配额管理

#### 获取组织配额

```http
GET /api/quotas?organization_id=1
Authorization: Bearer <access_token>
```

**响应** (200):

```json
[
  {
    "id": 1,
    "organization_id": 1,
    "resource_type": "projects",
    "limit": 100,
    "used": 45,
    "reset_at": null
  },
  {
    "id": 2,
    "organization_id": 1,
    "resource_type": "api_calls",
    "limit": 1000000,
    "used": 450000,
    "reset_at": "2025-12-01T00:00:00Z"
  }
]
```

#### 更新配额限制

```http
PUT /api/quotas/{quota_id}
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "limit": 200
}
```

**响应** (200):

```json
{
  "id": 1,
  "resource_type": "projects",
  "limit": 200,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

### 审计日志

#### 获取审计日志

```http
GET /api/audit-logs?organization_id=1&action=CREATE&days=7
Authorization: Bearer <access_token>
```

**查询参数**:

- `organization_id`: 组织ID
- `action`: 操作类型 (`CREATE`, `READ`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`)
- `resource_type`: 资源类型
- `user_id`: 用户ID
- `days`: 最近天数

**响应** (200):

```json
[
  {
    "id": 1,
    "action": "CREATE",
    "resource_type": "project",
    "resource_id": 5,
    "user_id": 10,
    "organization_id": 1,
    "description": "创建项目: 我的新项目",
    "changes": {...},
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2025-11-14T10:00:00Z"
  }
]
```

---

## 性能监控

### 获取监控仪表板

获取性能监控概览。

```http
GET /api/monitoring/dashboard/overview
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "active_workflows": 3,
  "success_rate": 95.5,
  "avg_completion_time_seconds": 450,
  "total_tokens_used_today": 125000,
  "cache_hit_rate": 0.65,
  "active_alerts": 2,
  "timestamp": "2025-11-14T10:00:00Z"
}
```

### 获取工作流统计

获取工作流执行统计。

```http
GET /api/monitoring/workflows/stats?project_id=1&days=7
Authorization: Bearer <access_token>
```

**查询参数**:

- `project_id`: 按项目筛选（可选）
- `days`: 统计天数（默认7天）

**响应** (200):

```json
{
  "total": 50,
  "successful": 47,
  "failed": 3,
  "avg_tokens": 25000,
  "avg_completion_time_seconds": 420,
  "cache_hit_rate": 0.65,
  "stage_timings": {
    "requirements_analysis": 120,
    "architecture_design": 180,
    "ui_design": 150,
    "development": 600,
    "testing": 240,
    "qa_review": 180,
    "completion": 30
  }
}
```

### 获取智能体性能

获取智能体性能统计。

```http
GET /api/monitoring/agents/summary?days=7
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "agents": [
    {
      "agent_name": "DeveloperAgent",
      "total_executions": 50,
      "successful_executions": 48,
      "failed_executions": 2,
      "avg_execution_time_seconds": 600,
      "avg_tokens_used": 15000,
      "cache_hit_rate": 0.70
    }
  ],
  "period_start": "2025-11-07T00:00:00Z",
  "period_end": "2025-11-14T00:00:00Z"
}
```

### 获取系统指标

获取系统资源使用情况。

```http
GET /api/monitoring/system/metrics
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "cpu_usage_percent": 45.5,
  "memory_usage_percent": 62.3,
  "disk_usage_percent": 38.7,
  "active_connections": 15,
  "requests_per_minute": 120,
  "timestamp": "2025-11-14T10:00:00Z"
}
```

### 获取LLM使用统计

获取LLM Token使用统计。

```http
GET /api/monitoring/llm/usage?days=30
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "total_tokens": 1250000,
  "total_cost": 125.50,
  "by_provider": [
    {
      "provider": "deepseek",
      "tokens": 1000000,
      "cost": 100.00,
      "percentage": 80
    },
    {
      "provider": "anthropic",
      "tokens": 250000,
      "cost": 25.50,
      "percentage": 20
    }
  ],
  "by_project": [
    {
      "project_id": 1,
      "project_name": "我的项目",
      "tokens": 50000,
      "cost": 5.00
    }
  ],
  "period_start": "2025-10-15T00:00:00Z",
  "period_end": "2025-11-14T00:00:00Z"
}
```

### 获取性能告警

获取活跃的性能告警。

```http
GET /api/monitoring/alerts?severity=high
Authorization: Bearer <access_token>
```

**查询参数**:

- `severity`: 严重程度 (`low`, `medium`, `high`, `critical`)
- `is_resolved`: 是否已解决

**响应** (200):

```json
[
  {
    "id": 1,
    "alert_type": "high_token_usage",
    "severity": "high",
    "message": "Token使用量超过阈值90%",
    "details": {
      "threshold": 0.9,
      "current_value": 0.92
    },
    "is_resolved": false,
    "created_at": "2025-11-14T09:30:00Z",
    "resolved_at": null
  }
]
```

### 创建性能告警

手动创建性能告警。

```http
POST /api/monitoring/alerts
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:

```json
{
  "alert_type": "custom",
  "severity": "medium",
  "message": "自定义告警消息",
  "details": {
    "custom_field": "value"
  }
}
```

**响应** (201):

```json
{
  "id": 2,
  "alert_type": "custom",
  "severity": "medium",
  "message": "自定义告警消息",
  "is_resolved": false,
  "created_at": "2025-11-14T10:00:00Z"
}
```

### 解决告警

标记告警为已解决。

```http
POST /api/monitoring/alerts/{alert_id}/resolve
Authorization: Bearer <access_token>
```

**响应** (200):

```json
{
  "id": 1,
  "is_resolved": true,
  "resolved_at": "2025-11-14T10:30:00Z"
}
```

---

## WebSocket

### 连接 WebSocket

使用 Socket.IO 连接到 WebSocket 服务器。

```javascript
import io from 'socket.io-client'

const socket = io('http://localhost:8000', {
  auth: {
    token: 'your_access_token'
  },
  transports: ['websocket']
})

// 连接成功
socket.on('connect', () => {
  console.log('Connected:', socket.id)
})

// 连接错误
socket.on('connect_error', (error) => {
  console.error('Connection error:', error)
})
```

### 订阅项目更新

订阅特定项目的实时更新。

```javascript
// 订阅项目
socket.emit('subscribe_project', {
  project_id: 1
})

// 接收项目更新
socket.on('project_update', (data) => {
  console.log('Project update:', data)
  // data: {
  //   project_id: 1,
  //   status: 'running',
  //   progress: 45,
  //   current_stage: 'development'
  // }
})

// 取消订阅
socket.emit('unsubscribe_project', {
  project_id: 1
})
```

### 接收智能体活动

实时接收智能体执行活动。

```javascript
socket.on('agent_activity', (data) => {
  console.log('Agent activity:', data)
  // data: {
  //   project_id: 1,
  //   agent_name: 'DeveloperAgent',
  //   stage: 'development',
  //   status: 'running',
  //   message: '正在生成代码...'
  // }
})
```

### 接收工作流事件

接收工作流的各种事件。

```javascript
// 工作流开始
socket.on('workflow_started', (data) => {
  console.log('Workflow started:', data)
})

// 阶段完成
socket.on('stage_completed', (data) => {
  console.log('Stage completed:', data)
  // data: {
  //   project_id: 1,
  //   stage: 'requirements_analysis',
  //   duration_seconds: 120,
  //   tokens_used: 3500
  // }
})

// 工作流完成
socket.on('workflow_completed', (data) => {
  console.log('Workflow completed:', data)
})

// 工作流失败
socket.on('workflow_failed', (data) => {
  console.error('Workflow failed:', data)
})
```

### 断开连接

```javascript
socket.disconnect()
```

---

## 附录

### A. HTTP 状态码完整列表

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 201 | Created | 资源创建成功 |
| 204 | No Content | 请求成功，无返回内容 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable Entity | 数据验证失败 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务不可用 |
| 504 | Gateway Timeout | 网关超时 |

### B. 工作流阶段列表

| 阶段 | 智能体 | 平均耗时 | 说明 |
|------|--------|---------|------|
| `requirements_analysis` | RequirementsAnalystAgent | 2分钟 | 需求分析 |
| `architecture_design` | ArchitectAgent | 3分钟 | 架构设计 |
| `ui_design` | UXUIDesignerAgent | 2.5分钟 | UI设计 |
| `development` | DeveloperAgent | 10分钟 | 代码开发 |
| `testing` | TestEngineerAgent | 4分钟 | 测试 |
| `qa_review` | QualityExpertAgent | 3分钟 | 质量评审 |
| `completion` | ProjectManagerAgent | 1分钟 | 完成交付 |

### C. LLM 提供商配置

| 提供商 | Provider值 | 默认模型 | API Base URL |
|--------|-----------|---------|--------------|
| DeepSeek | `deepseek` | `deepseek-chat` | `https://api.deepseek.com` |
| Anthropic | `anthropic` | `claude-3-sonnet` | `https://api.anthropic.com` |
| Google Gemini | `google` | `gemini-pro` | `https://generativelanguage.googleapis.com` |
| Moonshot | `moonshot` | `moonshot-v1` | `https://api.moonshot.cn` |
| Zhipu | `zhipu` | `glm-4` | `https://open.bigmodel.cn` |
| MiniMax | `minimax` | `abab5.5-chat` | `https://api.minimax.chat` |

### D. 错误码参考

| 错误码 | 说明 |
|--------|------|
| `AUTH_001` | 认证失败 |
| `AUTH_002` | Token过期 |
| `AUTH_003` | 权限不足 |
| `PROJ_001` | 项目不存在 |
| `PROJ_002` | 项目已在运行 |
| `PROJ_003` | 配额已满 |
| `FILE_001` | 文件过大 |
| `FILE_002` | 文件类型不支持 |
| `LLM_001` | LLM API调用失败 |
| `LLM_002` | LLM配置无效 |
| `WORKFLOW_001` | 工作流执行失败 |
| `PLUGIN_001` | 插件不兼容 |
| `PLUGIN_002` | 插件已安装 |

---

**文档版本**: v0.2.2
**最后更新**: 2025-11-14
**维护团队**: ResoftAI Development Team

如有问题或建议，请访问: https://github.com/yourusername/resoftai-cli/issues
