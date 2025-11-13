# ResoftAI 开发任务清单

**基于用户确认的技术方案**

---

## 核心技术决策 ✅

- **数据库**: PostgreSQL（生产级）
- **用户认证**: JWT Token（用户名密码登录）
- **部署环境**: 本地开发/演示
- **代码编辑器**: Monaco Editor（VS Code同款）
- **WebSocket**: Socket.io
- **图表库**: ECharts
- **状态管理**: Pinia

---

## Phase 1: 基础设施和认证系统（第1周）

### 任务1.1: 数据库设计和初始化 🔧

**优先级**: P0 - 最高
**预估时间**: 1天

#### 子任务
- [ ] 1.1.1 安装PostgreSQL依赖
  ```bash
  # 添加到requirements.txt
  sqlalchemy>=2.0.0
  asyncpg>=0.29.0
  alembic>=1.13.0
  psycopg2-binary>=2.9.0
  ```

- [ ] 1.1.2 创建数据库模型
  - 文件路径: `src/resoftai/models/`
  - 需要的表:
    - `users` - 用户表
    - `projects` - 项目表
    - `agents` - 智能体记录表
    - `tasks` - 任务表
    - `files` - 文件表
    - `file_versions` - 文件版本表
    - `llm_configs` - LLM配置表
    - `logs` - 系统日志表

- [ ] 1.1.3 创建数据库连接管理器
  - 文件: `src/resoftai/db/connection.py`
  - 实现连接池
  - 实现会话管理

- [ ] 1.1.4 初始化Alembic迁移
  ```bash
  alembic init alembic
  alembic revision --autogenerate -m "Initial schema"
  alembic upgrade head
  ```

- [ ] 1.1.5 创建种子数据脚本
  - 默认管理员账号
  - 示例项目数据

**数据库Schema设计**:
```sql
-- users表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',  -- admin, user, viewer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- projects表
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    requirements TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, planning, developing, testing, completed, failed
    progress INTEGER DEFAULT 0,
    current_stage VARCHAR(50),
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- agents表（记录智能体活动）
CREATE TABLE agent_activities (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    agent_role VARCHAR(50) NOT NULL,
    status VARCHAR(20),  -- idle, working, completed, failed
    current_task TEXT,
    completed_tasks INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tasks表
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    stage VARCHAR(50) NOT NULL,
    agent_role VARCHAR(50),
    description TEXT,
    status VARCHAR(20),  -- pending, in_progress, completed, failed
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- files表
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    path VARCHAR(500) NOT NULL,
    content TEXT,
    language VARCHAR(50),
    size INTEGER,
    current_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, path)
);

-- file_versions表
CREATE TABLE file_versions (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_id, version)
);

-- llm_configs表
CREATE TABLE llm_configs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100),
    provider VARCHAR(50) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    model_name VARCHAR(100),
    max_tokens INTEGER,
    temperature FLOAT,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- logs表
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    level VARCHAR(20),  -- debug, info, warning, error
    message TEXT,
    source VARCHAR(100),  -- agent_role or system component
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_agent_activities_project_id ON agent_activities(project_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_logs_project_id ON logs(project_id);
CREATE INDEX idx_logs_created_at ON logs(created_at);
```

---

### 任务1.2: 用户认证系统 🔐

**优先级**: P0 - 最高
**预估时间**: 1.5天

#### 子任务
- [ ] 1.2.1 安装JWT依赖
  ```bash
  # 添加到requirements.txt
  python-jose[cryptography]>=3.3.0
  passlib[bcrypt]>=1.7.4
  python-multipart>=0.0.6
  ```

- [ ] 1.2.2 创建认证工具类
  - 文件: `src/resoftai/auth/security.py`
  - 密码哈希/验证（bcrypt）
  - JWT Token生成/验证
  - Token刷新机制

- [ ] 1.2.3 创建用户模型和CRUD
  - 文件: `src/resoftai/models/user.py`
  - 文件: `src/resoftai/crud/user.py`
  - 创建用户
  - 验证用户
  - 更新用户信息

- [ ] 1.2.4 实现认证API端点
  - 文件: `src/resoftai/api/routes/auth.py`
  - POST `/api/auth/register` - 注册
  - POST `/api/auth/login` - 登录
  - POST `/api/auth/refresh` - 刷新Token
  - GET `/api/auth/me` - 获取当前用户信息
  - POST `/api/auth/logout` - 登出

- [ ] 1.2.5 创建认证依赖和中间件
  - 文件: `src/resoftai/auth/dependencies.py`
  - `get_current_user` - 验证Token并返回当前用户
  - `require_admin` - 要求管理员权限
  - `get_current_active_user` - 验证用户是否激活

- [ ] 1.2.6 更新现有API添加认证保护
  - Projects API需要认证
  - Agents API需要认证
  - Files API需要认证

**代码示例**:
```python
# src/resoftai/auth/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp: int = payload.get("exp")
        typ: str = payload.get("type")

        if username is None or typ != token_type:
            return None

        if datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        return TokenData(username=username)
    except JWTError:
        return None
```

```python
# src/resoftai/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.db.connection import get_db
from resoftai.models.user import User
from resoftai.crud.user import get_user_by_username
from resoftai.auth.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

---

### 任务1.3: Agent基类LLM抽象更新 🤖

**优先级**: P0 - 最高
**预估时间**: 0.5天

#### 子任务
- [ ] 1.3.1 更新Agent基类
  - 文件: `src/resoftai/core/agent.py`
  - 替换直接的Anthropic client为LLM Factory
  - 支持流式和非流式生成
  - 添加Token使用统计

- [ ] 1.3.2 更新7个专业智能体
  - 确保所有智能体继承更新后的Agent基类
  - 测试各智能体的LLM调用

- [ ] 1.3.3 更新示例代码
  - `examples/example_usage.py`
  - `examples/custom_extension.py`

- [ ] 1.3.4 编写单元测试
  - 测试不同provider的切换
  - 测试流式和非流式生成

**代码示例**:
```python
# src/resoftai/core/agent.py 更新
from typing import Optional, AsyncIterator
from resoftai.llm.factory import LLMFactory
from resoftai.llm.base import LLMConfig, LLMResponse
from resoftai.config import Settings

class Agent:
    """Updated Agent base class using LLM abstraction."""

    def __init__(
        self,
        role: AgentRole,
        message_bus: MessageBus,
        project_state: ProjectState,
        llm_config: Optional[LLMConfig] = None
    ):
        self.role = role
        self.message_bus = message_bus
        self.project_state = project_state

        # Use LLM Factory instead of direct Anthropic client
        config = llm_config or Settings().get_llm_config()
        self.llm = LLMFactory.create(config)

        # Statistics
        self.total_tokens = 0
        self.requests_count = 0

    async def generate(
        self,
        prompt: str,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Generate response using configured LLM."""
        if stream:
            return self.generate_stream(prompt, **kwargs)

        response: LLMResponse = await self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            **kwargs
        )

        # Update statistics
        self.total_tokens += response.total_tokens
        self.requests_count += 1

        # Publish event
        await self.message_bus.publish(AgentEvent(
            agent_role=self.role,
            event_type="generation_complete",
            data={
                "tokens": response.total_tokens,
                "model": response.model,
                "provider": response.provider.value
            }
        ))

        return response.content

    async def generate_stream(
        self,
        prompt: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response."""
        async for chunk in self.llm.generate_stream(
            prompt=prompt,
            system_prompt=self.system_prompt,
            **kwargs
        ):
            yield chunk

    async def execute(self, task: Task) -> TaskResult:
        """Execute task using LLM (to be implemented by subclasses)."""
        raise NotImplementedError
```

---

## Phase 2: WebSocket和后端API扩展（第1-2周）

### 任务2.1: WebSocket实时通信 📡

**优先级**: P0 - 最高
**预估时间**: 2天

#### 子任务
- [ ] 2.1.1 安装Socket.io依赖
  ```bash
  # 添加到requirements.txt
  python-socketio>=5.10.0
  ```

- [ ] 2.1.2 创建WebSocket管理器
  - 文件: `src/resoftai/websocket/manager.py`
  - 连接管理（连接、断开、房间管理）
  - 消息广播
  - 心跳检测

- [ ] 2.1.3 定义消息类型
  - 文件: `src/resoftai/websocket/events.py`
  - `project.progress` - 项目进度更新
  - `agent.status` - 智能体状态变化
  - `log.new` - 新日志消息
  - `task.complete` - 任务完成通知

- [ ] 2.1.4 集成到FastAPI
  - 文件: `src/resoftai/api/main.py`
  - 挂载Socket.io
  - 配置CORS

- [ ] 2.1.5 实现事件发布者
  - 在Agent执行任务时发布进度事件
  - 在Workflow状态变化时发布事件

**代码示例**:
```python
# src/resoftai/websocket/manager.py
import socketio
from typing import Dict, Set

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[str]] = {}

    async def connect(self, sid: str, project_id: str):
        """Add connection to project room."""
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(sid)
        await sio.enter_room(sid, f"project:{project_id}")

    async def disconnect(self, sid: str):
        """Remove connection."""
        for project_id, sids in self.active_connections.items():
            if sid in sids:
                sids.remove(sid)
                await sio.leave_room(sid, f"project:{project_id}")

    async def broadcast_to_project(self, project_id: str, event: str, data: dict):
        """Broadcast message to all clients in a project room."""
        await sio.emit(
            event,
            data,
            room=f"project:{project_id}"
        )

manager = ConnectionManager()

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    await manager.disconnect(sid)

@sio.event
async def join_project(sid, data):
    """Join a project room."""
    project_id = data.get('project_id')
    await manager.connect(sid, project_id)
    await sio.emit('joined', {'project_id': project_id}, room=sid)

@sio.event
async def leave_project(sid, data):
    """Leave a project room."""
    project_id = data.get('project_id')
    await sio.leave_room(sid, f"project:{project_id}")
```

```python
# src/resoftai/websocket/events.py
from typing import Literal, TypedDict
from datetime import datetime

class ProjectProgressEvent(TypedDict):
    type: Literal["project.progress"]
    project_id: str
    data: dict
    timestamp: str

class AgentStatusEvent(TypedDict):
    type: Literal["agent.status"]
    project_id: str
    agent_role: str
    data: dict
    timestamp: str

class LogEvent(TypedDict):
    type: Literal["log.new"]
    project_id: str
    data: dict
    timestamp: str

async def emit_progress(project_id: str, percentage: int, stage: str, message: str):
    """Emit project progress update."""
    from resoftai.websocket.manager import manager

    event: ProjectProgressEvent = {
        "type": "project.progress",
        "project_id": project_id,
        "data": {
            "percentage": percentage,
            "stage": stage,
            "message": message
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    await manager.broadcast_to_project(project_id, "project.progress", event)
```

---

### 任务2.2: 后端API扩展 🔌

**优先级**: P0 - 最高
**预估时间**: 2天

#### 子任务
- [ ] 2.2.1 扩展Projects API
  - GET `/api/projects` - 获取用户的项目列表（分页、筛选）
  - POST `/api/projects` - 创建新项目
  - GET `/api/projects/{id}` - 获取项目详情
  - PUT `/api/projects/{id}` - 更新项目
  - DELETE `/api/projects/{id}` - 删除项目
  - GET `/api/projects/{id}/tasks` - 获取项目任务列表
  - GET `/api/projects/{id}/artifacts` - 获取项目生成的文档

- [ ] 2.2.2 Agents API
  - GET `/api/agents` - 获取所有智能体状态
  - GET `/api/agents/{role}` - 获取单个智能体详情
  - GET `/api/agents/{role}/activities` - 获取智能体活动记录
  - GET `/api/projects/{id}/agents` - 获取项目的智能体状态

- [ ] 2.2.3 Files API
  - GET `/api/projects/{id}/files` - 获取项目文件树
  - GET `/api/files/{id}` - 获取文件内容
  - PUT `/api/files/{id}` - 更新文件内容（创建新版本）
  - GET `/api/files/{id}/versions` - 获取文件版本历史
  - POST `/api/files/{id}/restore/{version}` - 恢复到某个版本
  - GET `/api/projects/{id}/files/download` - 下载整个项目（ZIP）

- [ ] 2.2.4 Logs API
  - GET `/api/projects/{id}/logs` - 获取项目日志（分页）
  - POST `/api/logs` - 创建日志（内部API）

- [ ] 2.2.5 LLM Configs API
  - GET `/api/configs/llm` - 获取用户的LLM配置
  - POST `/api/configs/llm` - 创建新配置
  - PUT `/api/configs/llm/{id}` - 更新配置
  - DELETE `/api/configs/llm/{id}` - 删除配置
  - POST `/api/configs/llm/{id}/test` - 测试配置连接

**目录结构**:
```
src/resoftai/api/
├── __init__.py
├── main.py                   # FastAPI app
├── dependencies.py           # 共享依赖
└── routes/
    ├── __init__.py
    ├── auth.py              # 认证路由
    ├── projects.py          # 项目路由
    ├── agents.py            # 智能体路由
    ├── files.py             # 文件路由
    ├── logs.py              # 日志路由
    └── configs.py           # 配置路由
```

---

## Phase 3: 前端登录和布局（第2周）

### 任务3.1: 前端认证页面 🔐

**优先级**: P0 - 最高
**预估时间**: 1天

#### 子任务
- [ ] 3.1.1 创建Auth Store (Pinia)
  - 文件: `frontend/src/stores/auth.js`
  - 状态: user, token, isAuthenticated
  - Actions: login, logout, refresh, fetchUser

- [ ] 3.1.2 创建Login页面
  - 文件: `frontend/src/views/Login.vue`
  - 用户名/密码表单
  - 表单验证
  - 错误提示

- [ ] 3.1.3 创建Register页面（可选）
  - 文件: `frontend/src/views/Register.vue`
  - 注册表单
  - 密码强度检查
  - 邮箱验证

- [ ] 3.1.4 更新路由守卫
  - 文件: `frontend/src/router/index.js`
  - 未登录重定向到登录页
  - 登录后跳转到Dashboard

- [ ] 3.1.5 更新API客户端
  - 文件: `frontend/src/api/client.js`
  - Token自动刷新
  - 401错误自动登出

**代码示例**:
```javascript
// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { apiClient } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },

  actions: {
    async login(username, password) {
      const response = await apiClient.post('/auth/login', {
        username,
        password
      })

      this.token = response.access_token
      this.refreshToken = response.refresh_token

      localStorage.setItem('token', this.token)
      localStorage.setItem('refreshToken', this.refreshToken)

      await this.fetchUser()
    },

    async fetchUser() {
      const user = await apiClient.get('/auth/me')
      this.user = user
    },

    async logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
    },

    async refresh() {
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: this.refreshToken
      })

      this.token = response.access_token
      localStorage.setItem('token', this.token)
    }
  }
})
```

---

### 任务3.2: 前端依赖安装 📦

**优先级**: P0 - 最高
**预估时间**: 0.5天

#### 子任务
- [ ] 3.2.1 安装Monaco Editor
  ```bash
  npm install monaco-editor
  npm install @monaco-editor/react
  # 或者 Vue版本
  npm install @guolao/vue-monaco-editor
  ```

- [ ] 3.2.2 安装ECharts
  ```bash
  npm install echarts
  npm install vue-echarts
  ```

- [ ] 3.2.3 安装Socket.io客户端
  ```bash
  npm install socket.io-client
  ```

- [ ] 3.2.4 安装其他工具库
  ```bash
  npm install dayjs  # 时间处理
  npm install lodash-es  # 工具函数
  npm install @vueuse/core  # Vue组合式工具
  ```

---

## Phase 4: 前端核心页面开发（第2-3周）

### 任务4.1: Dashboard页面 📊

**优先级**: P0 - 最高
**预估时间**: 2天

#### 设计规格
- 统计卡片区（4个）
  - 项目总数
  - 进行中项目
  - 已完成项目
  - Token使用总量

- 智能体状态区（7个卡片）
  - 每个智能体显示：名称、状态、当前任务、Token使用

- 图表区
  - 项目进度趋势图（折线图）
  - Token使用分布（饼图）

- 最近项目列表
  - 最新5个项目
  - 点击跳转到详情

#### 子任务
- [ ] 4.1.1 创建统计卡片组件
  - 文件: `frontend/src/components/StatCard.vue`

- [ ] 4.1.2 创建智能体状态卡片组件
  - 文件: `frontend/src/components/AgentStatusCard.vue`

- [ ] 4.1.3 创建图表组件
  - 文件: `frontend/src/components/charts/ProjectTrend.vue`
  - 文件: `frontend/src/components/charts/TokenDistribution.vue`

- [ ] 4.1.4 组装Dashboard页面
  - 文件: `frontend/src/views/Dashboard.vue`
  - 数据获取
  - WebSocket实时更新

- [ ] 4.1.5 创建Dashboard Store
  - 文件: `frontend/src/stores/dashboard.js`

**组件示例**:
```vue
<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <stat-card
          title="项目总数"
          :value="stats.totalProjects"
          icon="FolderOpened"
          color="#409eff"
        />
      </el-col>
      <el-col :span="6">
        <stat-card
          title="进行中"
          :value="stats.activeProjects"
          icon="Loading"
          color="#67c23a"
        />
      </el-col>
      <el-col :span="6">
        <stat-card
          title="已完成"
          :value="stats.completedProjects"
          icon="CircleCheck"
          color="#409eff"
        />
      </el-col>
      <el-col :span="6">
        <stat-card
          title="Token使用"
          :value="formatNumber(stats.totalTokens)"
          icon="CreditCard"
          color="#e6a23c"
        />
      </el-col>
    </el-row>

    <!-- 智能体状态 -->
    <el-card class="agents-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>智能体状态</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col
          v-for="agent in agents"
          :key="agent.role"
          :span="24 / 7"
        >
          <agent-status-card :agent="agent" />
        </el-col>
      </el-row>
    </el-card>

    <!-- 图表 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <span>项目进度趋势</span>
          </template>
          <project-trend-chart :data="trendData" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never">
          <template #header>
            <span>Token使用分布</span>
          </template>
          <token-distribution-chart :data="tokenData" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近项目 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>最近项目</span>
          <el-button type="primary" link @click="$router.push('/projects')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      <el-table :data="recentProjects" stripe>
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="$router.push(`/projects/${row.id}`)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useWebSocket } from '@/composables/useWebSocket'
import StatCard from '@/components/StatCard.vue'
import AgentStatusCard from '@/components/AgentStatusCard.vue'
import ProjectTrendChart from '@/components/charts/ProjectTrend.vue'
import TokenDistributionChart from '@/components/charts/TokenDistribution.vue'

const dashboardStore = useDashboardStore()
const { socket, connect, disconnect } = useWebSocket()

const stats = ref({
  totalProjects: 0,
  activeProjects: 0,
  completedProjects: 0,
  totalTokens: 0
})

const agents = ref([])
const recentProjects = ref([])
const trendData = ref([])
const tokenData = ref([])

onMounted(async () => {
  // 加载数据
  await loadDashboardData()

  // 连接WebSocket
  connect()

  // 监听实时更新
  socket.value?.on('dashboard.update', (data) => {
    updateDashboardData(data)
  })
})

onUnmounted(() => {
  disconnect()
})

async function loadDashboardData() {
  const data = await dashboardStore.fetchDashboardData()
  stats.value = data.stats
  agents.value = data.agents
  recentProjects.value = data.recentProjects
  trendData.value = data.trendData
  tokenData.value = data.tokenData
}

function updateDashboardData(data) {
  // 实时更新数据
  if (data.type === 'stats') {
    stats.value = { ...stats.value, ...data.data }
  } else if (data.type === 'agent') {
    const index = agents.value.findIndex(a => a.role === data.role)
    if (index !== -1) {
      agents.value[index] = { ...agents.value[index], ...data.data }
    }
  }
}
</script>
```

---

### 任务4.2: Projects页面 📁

**优先级**: P0 - 最高
**预估时间**: 2天

#### 设计规格
- 工具栏
  - 新建项目按钮
  - 搜索框（按名称搜索）
  - 筛选器（状态、AI模型、时间范围）
  - 视图切换（表格/卡片）

- 项目列表
  - 表格视图：名称、状态、进度、AI模型、创建时间、操作
  - 卡片视图：项目卡片（名称、状态、进度、快捷操作）

- 创建项目对话框
  - 项目名称
  - 需求描述（大文本框）
  - AI模型选择
  - 高级选项（折叠）

- 分页
  - 每页20条
  - 页码跳转

#### 子任务
- [ ] 4.2.1 创建项目卡片组件
  - 文件: `frontend/src/components/ProjectCard.vue`

- [ ] 4.2.2 创建项目创建对话框
  - 文件: `frontend/src/components/CreateProjectDialog.vue`

- [ ] 4.2.3 创建Projects页面
  - 文件: `frontend/src/views/Projects.vue`

- [ ] 4.2.4 创建Projects Store
  - 文件: `frontend/src/stores/projects.js`

**页面示例**:
```vue
<!-- frontend/src/views/Projects.vue -->
<template>
  <div class="projects-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>

      <div class="toolbar-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目..."
          :prefix-icon="Search"
          style="width: 300px"
          clearable
          @input="handleSearch"
        />

        <el-select
          v-model="filterStatus"
          placeholder="状态"
          clearable
          style="width: 150px"
          @change="handleFilter"
        >
          <el-option label="全部" value="" />
          <el-option label="待开始" value="pending" />
          <el-option label="进行中" value="developing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>

        <el-button-group>
          <el-button
            :type="viewMode === 'table' ? 'primary' : ''"
            @click="viewMode = 'table'"
          >
            <el-icon><Grid /></el-icon>
          </el-button>
          <el-button
            :type="viewMode === 'card' ? 'primary' : ''"
            @click="viewMode = 'card'"
          >
            <el-icon><Menu /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 表格视图 -->
    <el-table
      v-if="viewMode === 'table'"
      :data="projects"
      stripe
      v-loading="loading"
    >
      <el-table-column prop="name" label="项目名称" min-width="200" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度" width="200">
        <template #default="{ row }">
          <el-progress :percentage="row.progress" />
        </template>
      </el-table-column>
      <el-table-column prop="llm_provider" label="AI模型" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.llm_provider }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            @click="$router.push(`/projects/${row.id}`)"
          >
            查看
          </el-button>
          <el-button type="warning" link>编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 卡片视图 -->
    <el-row v-else :gutter="20" v-loading="loading">
      <el-col
        v-for="project in projects"
        :key="project.id"
        :span="8"
      >
        <project-card
          :project="project"
          @view="$router.push(`/projects/${project.id}`)"
          @delete="handleDelete(project)"
        />
      </el-col>
    </el-row>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 创建项目对话框 -->
    <create-project-dialog
      v-model="showCreateDialog"
      @success="handleCreateSuccess"
    />
  </div>
</template>
```

---

### 任务4.3-4.6: 其他页面（详细任务清单见下）

由于篇幅限制，其他页面（ProjectDetail、Agents、Files、Models）的详细任务清单将在单独的文档中列出。

---

## 依赖更新汇总

### 后端 requirements.txt
```txt
# 现有依赖
anthropic>=0.40.0
click>=8.1.0
rich>=13.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pyyaml>=6.0
jinja2>=3.1.0
fastapi>=0.104.0
uvicorn>=0.24.0
aiofiles>=23.0.0
python-dotenv>=1.0.0
httpx>=0.25.0

# 新增依赖 - 数据库
sqlalchemy>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
psycopg2-binary>=2.9.0

# 新增依赖 - 认证
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# 新增依赖 - WebSocket
python-socketio>=5.10.0

# Development dependencies
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.5.0
```

### 前端 package.json
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.6.0",

    "@guolao/vue-monaco-editor": "^1.3.0",
    "echarts": "^5.4.0",
    "vue-echarts": "^6.6.0",
    "socket.io-client": "^4.6.0",
    "dayjs": "^1.11.0",
    "lodash-es": "^4.17.21",
    "@vueuse/core": "^10.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

---

## 下一步行动

请确认以上开发计划是否符合预期。我将：

1. **立即开始** - 如果你同意，我现在就开始实现：
   - 先完成数据库模型设计
   - 然后实现用户认证系统
   - 再更新Agent基类

2. **调整计划** - 如果你想修改某些部分，请告诉我

3. **查看更多细节** - 我可以展开某个具体任务的更详细实现方案

你希望我如何继续？
