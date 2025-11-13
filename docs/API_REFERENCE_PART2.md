# ResoftAI API 参考文档 (续)

## 文件管理 API

### 获取文件列表

获取项目的文件列表。

**端点**: `GET /api/files`

**Headers**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `project_id` (int): 项目 ID
- `type` (string): 文件类型过滤

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "requirements.md",
      "path": "/docs/requirements.md",
      "type": "markdown",
      "size": 2048,
      "project_id": 1,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "message": "获取文件列表成功",
  "success": true
}
```

### 获取文件内容

获取文件内容。

**端点**: `GET /api/files/{file_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "requirements.md",
    "path": "/docs/requirements.md",
    "type": "markdown",
    "content": "# 需求规格说明书\\n\\n## 项目概述\\n...",
    "size": 2048,
    "project_id": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "获取文件内容成功",
  "success": true
}
```

### 创建文件

创建新文件。

**端点**: `POST /api/files`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "new_file.py",
  "path": "/src/new_file.py",
  "type": "python",
  "content": "print('Hello, World!')",
  "project_id": 1
}
```

**响应**:
```json
{
  "data": {
    "id": 2,
    "name": "new_file.py",
    "path": "/src/new_file.py",
    "type": "python",
    "content": "print('Hello, World!')",
    "size": 24,
    "project_id": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "文件创建成功",
  "success": true
}
```

### 更新文件

更新文件内容。

**端点**: `PUT /api/files/{file_id}`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "updated_file.py",
  "content": "print('Hello, Updated World!')"
}
```

**响应**:
```json
{
  "data": {
    "id": 2,
    "name": "updated_file.py",
    "path": "/src/updated_file.py",
    "type": "python",
    "content": "print('Hello, Updated World!')",
    "size": 32,
    "updated_at": "2024-01-01T01:00:00"
  },
  "message": "文件更新成功",
  "success": true
}
```

### 删除文件

删除指定文件。

**端点**: `DELETE /api/files/{file_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "文件删除成功",
  "success": true
}
```

### 获取文件版本历史

获取文件的版本历史。

**端点**: `GET /api/files/{file_id}/versions`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "file_id": 2,
      "version": 1,
      "content": "print('Hello, World!')",
      "created_at": "2024-01-01T00:00:00"
    },
    {
      "id": 2,
      "file_id": 2,
      "version": 2,
      "content": "print('Hello, Updated World!')",
      "created_at": "2024-01-01T01:00:00"
    }
  ],
  "message": "获取文件版本历史成功",
  "success": true
}
```

### 恢复文件版本

恢复文件到指定版本。

**端点**: `POST /api/files/{file_id}/restore/{version}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 2,
    "name": "updated_file.py",
    "path": "/src/updated_file.py",
    "type": "python",
    "content": "print('Hello, World!')",
    "size": 24,
    "updated_at": "2024-01-01T02:00:00"
  },
  "message": "文件版本恢复成功",
  "success": true
}
```

## LLM 配置 API

### 获取 LLM 配置列表

获取用户的 LLM 配置列表。

**端点**: `GET /api/llm-configs`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "DeepSeek 配置",
      "provider": "deepseek",
      "model_name": "deepseek-chat",
      "api_key": "sk-***",
      "max_tokens": 4096,
      "temperature": 0.7,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "message": "获取 LLM 配置列表成功",
  "success": true
}
```

### 创建 LLM 配置

创建新的 LLM 配置。

**端点**: `POST /api/llm-configs`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "Anthropic 配置",
  "provider": "anthropic",
  "api_key": "your-anthropic-api-key",
  "model_name": "claude-3-sonnet-20240229",
  "max_tokens": 4096,
  "temperature": 0.7
}
```

**响应**:
```json
{
  "data": {
    "id": 2,
    "name": "Anthropic 配置",
    "provider": "anthropic",
    "model_name": "claude-3-sonnet-20240229",
    "api_key": "sk-***",
    "max_tokens": 4096,
    "temperature": 0.7,
    "is_active": false,
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "LLM 配置创建成功",
  "success": true
}
```

### 获取 LLM 配置详情

获取指定 LLM 配置的详细信息。

**端点**: `GET /api/llm-configs/{config_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "DeepSeek 配置",
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "api_key": "sk-***",
    "max_tokens": 4096,
    "temperature": 0.7,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "获取 LLM 配置详情成功",
  "success": true
}
```

### 更新 LLM 配置

更新 LLM 配置信息。

**端点**: `PUT /api/llm-configs/{config_id}`

**Headers**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "name": "更新后的配置名称",
  "model_name": "deepseek-coder",
  "max_tokens": 8192
}
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "更新后的配置名称",
    "provider": "deepseek",
    "model_name": "deepseek-coder",
    "api_key": "sk-***",
    "max_tokens": 8192,
    "temperature": 0.7,
    "is_active": true,
    "updated_at": "2024-01-01T01:00:00"
  },
  "message": "LLM 配置更新成功",
  "success": true
}
```

### 删除 LLM 配置

删除指定 LLM 配置。

**端点**: `DELETE /api/llm-configs/{config_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "LLM 配置删除成功",
  "success": true
}
```

### 激活 LLM 配置

激活指定的 LLM 配置。

**端点**: `POST /api/llm-configs/{config_id}/activate`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "DeepSeek 配置",
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "is_active": true,
    "updated_at": "2024-01-01T01:00:00"
  },
  "message": "LLM 配置激活成功",
  "success": true
}
```

### 测试 LLM 配置

测试 LLM 配置的连接和可用性。

**端点**: `POST /api/llm-configs/{config_id}/test`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "success": true,
    "response_time": 1.23,
    "model_info": {
      "model": "deepseek-chat",
      "provider": "deepseek"
    }
  },
  "message": "LLM 配置测试成功",
  "success": true
}
```

### 获取活跃配置

获取当前活跃的 LLM 配置。

**端点**: `GET /api/llm-configs/active`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "name": "DeepSeek 配置",
    "provider": "deepseek",
    "model_name": "deepseek-chat",
    "api_key": "sk-***",
    "max_tokens": 4096,
    "temperature": 0.7,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "获取活跃配置成功",
  "success": true
}
```