# ResoftAI Quick Start Guide

快速启动ResoftAI多智能体软件开发平台。

---

## 🚀 最快启动方式（使用Docker）

### 1. 启动PostgreSQL

```bash
# 使用Docker Compose启动PostgreSQL
docker-compose up -d postgres

# 或使用docker run
docker run -d \
  --name resoftai-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resoftai \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件（必须配置LLM API Key）
nano .env
```

### 3. 初始化数据库

```bash
# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库和创建默认管理员
python scripts/init_db.py
```

### 4. 启动系统

**方式1: 使用启动脚本（推荐）**

```bash
# 同时启动前后端（使用tmux）
bash scripts/start_all.sh

# 或分别启动
bash scripts/start_backend.sh  # 终端1
bash scripts/start_frontend.sh  # 终端2
```

**方式2: 手动启动**

```bash
# 终端1 - 启动后端
uvicorn resoftai.api.main:asgi_app --reload --host 0.0.0.0 --port 8000

# 终端2 - 启动前端
cd frontend
npm install  # 首次运行
npm run dev
```

### 5. 访问系统

- **前端界面**: http://localhost:5173
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 6. 登录

使用默认管理员账户：
- **用户名**: `admin`
- **密码**: `admin123`

---

## 📋 详细步骤

### 前置要求

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 16+ (或使用Docker)
- **可选**: Docker, Docker Compose

### 环境配置

#### .env 配置说明

```bash
# LLM提供商配置（必须）
LLM_PROVIDER=deepseek  # anthropic, deepseek, zhipu, moonshot, minimax, google
LLM_API_KEY=your_api_key_here  # ⚠️ 必须配置
LLM_MODEL=deepseek-chat
LLM_MAX_TOKENS=8192
LLM_TEMPERATURE=0.7

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resoftai

# JWT认证配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API服务器配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_ENABLE_WEBSOCKET=true
```

### 数据库初始化

`scripts/init_db.py` 会自动：
1. 创建所有数据库表
2. 创建默认管理员用户（admin/admin123）
3. 验证数据库连接

```bash
python scripts/init_db.py
```

### API端点

#### 认证端点
- `POST /api/auth/register` - 注册新用户
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新Token
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 登出

#### 项目端点
- `GET /api/projects` - 列出项目
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

#### 智能体活动端点
- `GET /api/agent-activities` - 列出智能体活动
- `GET /api/agent-activities/active` - 获取活跃智能体
- `GET /api/agent-activities/{id}` - 获取活动详情
- `POST /api/agent-activities` - 创建活动记录
- `PUT /api/agent-activities/{id}` - 更新活动
- `DELETE /api/agent-activities/{id}` - 删除活动

#### 文件管理端点
- `GET /api/files?project_id=X` - 列出项目文件
- `GET /api/files/{id}` - 获取文件内容
- `POST /api/files` - 创建文件
- `PUT /api/files/{id}` - 更新文件（创建新版本）
- `DELETE /api/files/{id}` - 删除文件
- `GET /api/files/{id}/versions` - 获取文件历史版本
- `GET /api/files/{id}/versions/{version}` - 获取特定版本
- `POST /api/files/{id}/restore/{version}` - 恢复到指定版本

#### LLM配置端点
- `GET /api/llm-configs` - 列出LLM配置
- `GET /api/llm-configs/active` - 获取当前激活的配置
- `GET /api/llm-configs/{id}` - 获取配置详情
- `POST /api/llm-configs` - 创建LLM配置
- `PUT /api/llm-configs/{id}` - 更新配置
- `POST /api/llm-configs/{id}/activate` - 激活配置
- `DELETE /api/llm-configs/{id}` - 删除配置
- `POST /api/llm-configs/{id}/test` - 测试LLM连接

### WebSocket事件

连接: `http://localhost:8000/socket.io`

支持的事件：
- `project.progress` - 项目进度更新
- `agent.status` - 智能体状态变化
- `task.update` - 任务状态更新
- `log.new` - 新日志产生
- `file.change` - 文件变更

客户端操作：
- `join_project` - 加入项目房间
- `leave_project` - 离开项目房间
- `ping` - 心跳检测

---

## 🔧 故障排除

### PostgreSQL连接失败

```bash
# 检查PostgreSQL是否运行
pg_isready

# 使用Docker启动
docker-compose up -d postgres

# 检查容器日志
docker logs resoftai-postgres
```

### Python依赖问题

```bash
# 使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 前端依赖问题

```bash
cd frontend

# 清除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### JWT认证错误

如果遇到cryptography相关错误：

```bash
# 方案1: 重新安装cryptography
pip install --upgrade --force-reinstall cryptography cffi

# 方案2: 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 端口被占用

```bash
# 检查端口占用
lsof -i :8000  # 后端
lsof -i :5173  # 前端
lsof -i :5432  # PostgreSQL

# 杀死进程
kill -9 <PID>
```

---

## 📚 更多文档

- **后端设置**: `BACKEND_SETUP.md`
- **已知问题**: `KNOWN_ISSUES.md`
- **开发会话总结**: `SESSION_SUMMARY.md`
- **开发任务**: `docs/development-tasks.md`

---

## 🎯 下一步

1. **配置LLM API Key** - 在.env中配置您的API密钥
2. **创建项目** - 在前端界面创建第一个项目
3. **配置LLM** - 在"模型配置"页面添加和测试LLM
4. **开始开发** - 让AI智能体帮您开发软件！

---

## 💡 提示

- 首次使用建议先测试LLM连接（模型配置页面）
- 可以创建多个LLM配置，在不同项目中切换使用
- WebSocket实时更新需要前后端都在运行
- 查看 http://localhost:8000/docs 了解完整API文档

---

**祝您使用愉快！** 🎉
