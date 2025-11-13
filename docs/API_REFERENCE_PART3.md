# ResoftAI API 参考文档 (续)

## 执行控制 API

### 启动项目执行

启动指定项目的执行流程。

**端点**: `POST /api/execution/{project_id}/start`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "project_id": 1,
    "status": "running",
    "current_stage": "requirements_analysis",
    "started_at": "2024-01-01T00:00:00"
  },
  "message": "项目执行已启动",
  "success": true
}
```

### 停止项目执行

停止指定项目的执行流程。

**端点**: `POST /api/execution/{project_id}/stop`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "project_id": 1,
    "status": "stopped",
    "current_stage": "development",
    "stopped_at": "2024-01-01T01:00:00"
  },
  "message": "项目执行已停止",
  "success": true
}
```

### 获取执行状态

获取指定项目的执行状态。

**端点**: `GET /api/execution/{project_id}/status`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "project_id": 1,
    "status": "running",
    "current_stage": "development",
    "progress": 60,
    "started_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T01:00:00",
    "stages": [
      {
        "name": "requirements_analysis",
        "status": "completed",
        "completed_at": "2024-01-01T00:15:00"
      },
      {
        "name": "architecture_design",
        "status": "completed",
        "completed_at": "2024-01-01T00:30:00"
      },
      {
        "name": "ui_design",
        "status": "completed",
        "completed_at": "2024-01-01T00:45:00"
      },
      {
        "name": "development",
        "status": "in_progress",
        "started_at": "2024-01-01T00:45:00"
      },
      {
        "name": "testing",
        "status": "pending"
      },
      {
        "name": "quality_assurance",
        "status": "pending"
      },
      {
        "name": "completed",
        "status": "pending"
      }
    ]
  },
  "message": "获取执行状态成功",
  "success": true
}
```

### 获取项目工件

获取项目执行过程中生成的所有工件。

**端点**: `GET /api/execution/{project_id}/artifacts`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "project_id": 1,
    "artifacts": [
      {
        "type": "document",
        "name": "需求规格说明书",
        "file_id": 1,
        "created_at": "2024-01-01T00:15:00"
      },
      {
        "type": "document",
        "name": "系统架构设计",
        "file_id": 2,
        "created_at": "2024-01-01T00:30:00"
      },
      {
        "type": "code",
        "name": "后端 API 代码",
        "file_id": 3,
        "created_at": "2024-01-01T01:00:00"
      }
    ]
  },
  "message": "获取项目工件成功",
  "success": true
}
```

## 智能体活动 API

### 获取智能体活动列表

获取所有智能体活动记录。

**端点**: `GET /api/agent-activities`

**Headers**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `project_id` (int): 项目 ID 过滤
- `agent_type` (string): 智能体类型过滤
- `status` (string): 活动状态过滤

**响应**:
```json
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "agent_type": "requirements_analyst",
      "status": "completed",
      "input": "项目需求描述",
      "output": "需求规格说明书内容",
      "started_at": "2024-01-01T00:00:00",
      "completed_at": "2024-01-01T00:15:00",
      "execution_time": 900
    }
  ],
  "message": "获取智能体活动列表成功",
  "success": true
}
```

### 获取活跃活动

获取当前正在执行的智能体活动。

**端点**: `GET /api/agent-activities/active`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": [
    {
      "id": 5,
      "project_id": 1,
      "agent_type": "developer",
      "status": "in_progress",
      "input": "系统设计文档",
      "started_at": "2024-01-01T00:45:00",
      "current_progress": 75
    }
  ],
  "message": "获取活跃活动成功",
  "success": true
}
```

### 获取活动详情

获取指定智能体活动的详细信息。

**端点**: `GET /api/agent-activities/{activity_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "id": 1,
    "project_id": 1,
    "agent_type": "requirements_analyst",
    "status": "completed",
    "input": "开发一个支持用户注册、任务创建、分配和追踪的 Web 应用",
    "output": "# 需求规格说明书\\n\\n## 1. 项目概述\\n...",
    "started_at": "2024-01-01T00:00:00",
    "completed_at": "2024-01-01T00:15:00",
    "execution_time": 900,
    "files_generated": [1],
    "metrics": {
      "tokens_used": 1500,
      "api_calls": 3,
      "success_rate": 1.0
    }
  },
  "message": "获取活动详情成功",
  "success": true
}
```

## 监控 API

### 获取系统指标

获取系统性能指标和统计信息。

**端点**: `GET /api/monitoring/metrics`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "request_count": 150,
    "average_response_time": 0.23,
    "active_agents": 2,
    "completed_projects": 5,
    "failed_requests": 3,
    "uptime": 86400,
    "memory_usage": 256.5,
    "cpu_usage": 15.2,
    "database_connections": 3,
    "metrics_timestamp": "2024-01-01T12:00:00"
  },
  "message": "获取系统指标成功",
  "success": true
}
```

### 获取智能体活动统计

获取智能体活动统计信息。

**端点**: `GET /api/monitoring/agent-activities`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": [
    {
      "agent_type": "requirements_analyst",
      "total_activities": 10,
      "completed": 8,
      "failed": 2,
      "average_execution_time": 850,
      "success_rate": 0.8
    },
    {
      "agent_type": "developer",
      "total_activities": 15,
      "completed": 14,
      "failed": 1,
      "average_execution_time": 1200,
      "success_rate": 0.93
    }
  ],
  "message": "获取智能体活动统计成功",
  "success": true
}
```

### 获取完整监控状态

获取完整的系统监控状态。

**端点**: `GET /api/monitoring/status`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "data": {
    "system": {
      "status": "healthy",
      "uptime": 86400,
      "memory_usage": 256.5,
      "cpu_usage": 15.2,
      "disk_usage": 45.8
    },
    "database": {
      "status": "connected",
      "connections": 3,
      "query_count": 1250
    },
    "api": {
      "total_requests": 150,
      "success_rate": 0.98,
      "average_response_time": 0.23
    },
    "agents": {
      "total_activities": 25,
      "active_agents": 2,
      "success_rate": 0.88
    },
    "projects": {
      "total": 8,
      "completed": 5,
      "in_progress": 2,
      "failed": 1
    }
  },
  "message": "获取监控状态成功",
  "success": true
}
```

### 重置监控数据

重置监控指标数据。

**端点**: `POST /api/monitoring/reset`

**Headers**:
```
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "message": "监控数据重置成功",
  "success": true
}
```

## 系统 API

### 健康检查

检查系统健康状态。

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "service": "resoftai-api",
  "timestamp": "2024-01-01T12:00:00",
  "version": "0.2.1"
}
```

### API 文档

获取交互式 API 文档。

**端点**: `GET /docs`

**响应**: HTML 页面 (Swagger UI)

### ReDoc 文档

获取 ReDoc API 文档。

**端点**: `GET /redoc`

**响应**: HTML 页面 (ReDoc)

## WebSocket API

### 连接 WebSocket

连接到实时事件 WebSocket。

**端点**: `ws://localhost:8000/ws`

**认证**: 需要在连接时提供 JWT Token

**连接参数**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws', {
  headers: {
    'Authorization': 'Bearer <access_token>'
  }
});
```

### 事件类型

#### 项目状态更新
```json
{
  "type": "project_status_update",
  "data": {
    "project_id": 1,
    "status": "running",
    "current_stage": "development",
    "progress": 60
  }
}
```

#### 智能体活动开始
```json
{
  "type": "agent_activity_started",
  "data": {
    "activity_id": 5,
    "project_id": 1,
    "agent_type": "developer",
    "started_at": "2024-01-01T00:45:00"
  }
}
```

#### 智能体活动完成
```json
{
  "type": "agent_activity_completed",
  "data": {
    "activity_id": 5,
    "project_id": 1,
    "agent_type": "developer",
    "completed_at": "2024-01-01T01:00:00",
    "execution_time": 900
  }
}
```

#### 文件生成
```json
{
  "type": "file_generated",
  "data": {
    "file_id": 3,
    "project_id": 1,
    "name": "main.py",
    "path": "/src/main.py",
    "type": "python"
  }
}
```

#### 错误事件
```json
{
  "type": "error",
  "data": {
    "message": "LLM API 调用失败",
    "error_type": "api_error",
    "timestamp": "2024-01-01T00:30:00"
  }
}
```

---

**注意**: 所有 API 端点都需要有效的 JWT 访问令牌。请确保在请求头中包含 `Authorization: Bearer <access_token>`。