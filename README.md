# ResoftAI - 多智能体软件开发协作平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)

> AI驱动的软件定制开发服务平台，通过多智能体协作自动化完成从需求到交付的全流程

## 📋 项目简介

ResoftAI 是一个创新的多智能体协作平台，专为软件定制开发服务而设计。平台集成了7个专业AI智能体，模拟真实软件开发团队的协作模式，能够自动化完成从需求收集到最终交付的整个软件开发生命周期。

### 核心特性

- **🤖 7个专业AI智能体**
  - 项目经理 (Project Manager)
  - 需求分析师 (Requirements Analyst)
  - 软件架构师 (Software Architect)
  - UX/UI设计师 (UX/UI Designer)
  - 开发工程师 (Developer) - **增强版，支持代码质量检查**
  - 测试工程师 (Test Engineer)
  - 质量专家 (Quality Expert)

- **📊 完整的工作流引擎**
  - 7阶段工作流编排器
  - 需求分析 → 架构设计 → UI设计 → 开发 → 测试 → QA审核 → 完成
  - 支持迭代开发和阶段跳过
  - 实时进度跟踪和WebSocket推送
  - 完整的状态持久化

- **💾 强大的数据管理**
  - SQLite/PostgreSQL双数据库支持
  - 完整的项目版本控制
  - 文件版本历史和恢复
  - 智能体活动跟踪
  - 详细的日志记录

- **📚 全套文档自动生成**
  - 需求规格说明书 (SRS)
  - 系统设计文档
  - 数据库设计文档
  - 部署安装指南
  - 用户使用手册
  - 培训手册

- **🎯 多种交互方式**
  - RESTful Web API (32个端点)
  - Vue 3 前端界面
  - Monaco编辑器集成
  - WebSocket实时通信
  - CLI命令行工具

- **📦 项目模板系统** 🆕
  - **3个内置模板**: FastAPI REST API, React+FastAPI Web App, Python CLI Tool
  - **模板API**: 列表、详情、预览、应用
  - **变量系统**: 支持类型验证、默认值、必填项
  - **WebSocket实时反馈**: 应用进度实时推送
  - **多种过滤**: 按分类、标签筛选模板

- **✨ 代码质量保证系统** 🆕
  - **多语言代码质量检查** (支持9种编程语言)
  - **安全漏洞自动检测** (硬编码密码、SQL注入等)
  - **最佳实践验证** (代码规范、命名约定)
  - **质量评分系统** (0-100分自动评分)
  - **迭代式代码优化** (自动改进代码质量)

- **🌍 多语言支持系统** 🆕
  - **9种编程语言支持**: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP, Ruby
  - **语言特定最佳实践库** (编码标准、命名规范、安全实践)
  - **智能语言检测** (自动识别项目所需语言)
  - **框架推荐系统** (为每种语言推荐合适的框架)

## 🏗️ 系统架构

```
resoftai-cli/
├── src/resoftai/
│   ├── core/                    # 核心组件
│   │   ├── agent.py            # 智能体基类
│   │   ├── workflow.py         # 工作流引擎
│   │   ├── message_bus.py      # 消息总线
│   │   └── state.py            # 状态管理
│   ├── agents/                  # 专业智能体
│   │   ├── project_manager.py
│   │   ├── requirements_analyst.py
│   │   ├── architect.py
│   │   ├── uxui_designer.py
│   │   ├── developer.py
│   │   ├── test_engineer.py
│   │   └── quality_expert.py
│   ├── orchestration/          # 工作流编排
│   │   ├── workflow.py         # 工作流编排器
│   │   └── executor.py         # 项目执行器
│   ├── api/                     # Web API
│   │   ├── main.py             # FastAPI应用
│   │   └── routes/             # API路由
│   │       ├── auth.py
│   │       ├── projects.py
│   │       ├── files.py
│   │       ├── llm_configs.py
│   │       ├── agent_activities.py
│   │       ├── execution.py
│   │       └── templates.py    # 模板API 🆕
│   ├── models/                  # 数据模型
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── file.py
│   │   ├── llm_config.py
│   │   └── agent_activity.py
│   ├── crud/                    # 数据库操作
│   ├── auth/                    # 认证授权
│   ├── llm/                     # LLM抽象层
│   │   ├── factory.py          # LLM工厂
│   │   └── providers/          # LLM提供商
│   │       ├── deepseek_provider.py
│   │       ├── anthropic_provider.py
│   │       └── ...
│   ├── generators/              # 文档生成器
│   ├── templates/               # 项目模板 🆕
│   │   ├── base.py             # 模板基类
│   │   ├── manager.py          # 模板管理器
│   │   └── registry.py         # 内置模板注册
│   ├── websocket/               # WebSocket管理
│   ├── cli/                     # CLI界面
│   └── config/                  # 配置管理
├── frontend/                    # Vue 3前端
│   ├── src/
│   │   ├── components/         # 组件
│   │   │   ├── MonacoEditor.vue
│   │   │   └── FileEditor.vue
│   │   ├── views/              # 页面
│   │   ├── router/             # 路由
│   │   └── store/              # 状态管理
│   └── package.json
├── tests/                       # 测试用例
│   ├── test_llm_factory.py
│   ├── test_workflow.py
│   ├── test_agents.py
│   ├── test_api_integration.py
│   └── conftest.py
├── scripts/                     # 脚本
│   ├── init_db.py              # 数据库初始化
│   ├── start_backend.sh
│   └── start_frontend.sh
├── alembic/                     # 数据库迁移
├── .github/workflows/           # CI/CD 🆕
│   └── ci.yml                  # GitHub Actions workflow
├── Dockerfile                   # Docker容器化 🆕
├── docker-compose.yml           # Docker Compose配置
└── docs/                        # 文档
```

## 🚀 快速开始

### 环境要求

- Python 3.11 或更高版本
- Node.js 16+ (前端开发)
- PostgreSQL 12+ 或 SQLite (数据库)
- DeepSeek / Anthropic API密钥

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli
```

#### 2. 后端设置

```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.sqlite .env  # 使用SQLite
# 或者配置PostgreSQL
# cp .env.example .env

# 编辑 .env 文件，添加API密钥
nano .env
```

环境变量配置示例：

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./resoftai.db

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM配置
DEEPSEEK_API_KEY=your-deepseek-api-key
# 或
ANTHROPIC_API_KEY=your-anthropic-api-key
```

#### 3. 初始化数据库

```bash
python scripts/init_db.py
```

输出示例：
```
🔧 Initializing database...
📁 Database models loaded:
   - User
   - Project
   - AgentActivity
   - Task
   - File
   - LLMConfig
   - Log

✅ Database initialized successfully!
📊 Tables created:
   - users
   - projects
   - files
   - llm_configs
   - agent_activities
   - tasks
   - logs
   - file_versions
```

#### 4. 启动后端服务

```bash
# 开发模式
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload --port 8000

# 或使用启动脚本
bash scripts/start_backend.sh
```

#### 5. 启动前端（可选）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或使用启动脚本
bash scripts/start_frontend.sh
```

#### 6. Docker部署（推荐）🆕

```bash
# 使用Docker Compose快速启动
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down
```

Docker部署包含：
- PostgreSQL数据库
- Redis缓存
- ResoftAI API服务器
- 自动健康检查
- 数据持久化

### 快速验证

```bash
# 1. 健康检查
curl http://localhost:8000/health
# 输出: {"status":"healthy","service":"resoftai-api"}

# 2. 查看API文档
open http://localhost:8000/docs

# 3. 运行测试
PYTHONPATH=src pytest tests/ -v
```

## 📖 使用指南

### 创建用户和LLM配置

```bash
# 注册用户
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'

# 登录获取token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePassword123"

# 创建LLM配置
curl -X POST "http://localhost:8000/api/llm-configs" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DeepSeek配置",
    "provider": "deepseek",
    "api_key": "your-api-key",
    "model_name": "deepseek-chat",
    "max_tokens": 4096,
    "temperature": 0.7
  }'
```

### 创建和执行项目

```bash
# 创建项目
curl -X POST "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "任务管理系统",
    "description": "一个现代化的任务管理系统",
    "requirements": "开发一个支持用户注册、任务创建、分配和追踪的Web应用"
  }'

# 启动项目执行
curl -X POST "http://localhost:8000/api/execution/{project_id}/start" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看执行状态
curl "http://localhost:8000/api/execution/{project_id}/status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取生成的工件
curl "http://localhost:8000/api/execution/{project_id}/artifacts" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 使用项目模板 🆕

```bash
# 列出所有模板
curl "http://localhost:8000/api/v1/templates" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按分类过滤
curl "http://localhost:8000/api/v1/templates?category=rest_api" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取模板详情
curl "http://localhost:8000/api/v1/templates/fastapi-rest-api" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 应用模板到项目
curl -X POST "http://localhost:8000/api/v1/templates/python-cli-tool/apply" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "variables": {
      "project_name": "my-awesome-cli",
      "description": "My CLI tool",
      "author": "Your Name",
      "command_name": "mycli"
    },
    "overwrite": false
  }'

# 监听WebSocket实时进度
# 连接到 ws://localhost:8000/socket.io
# 监听事件: template:apply:progress, template:apply:complete
```

## 📚 API文档

访问 `http://localhost:8000/docs` 查看完整的交互式API文档。

### 主要API端点 (32个)

#### 认证 API
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户

#### 项目管理 API
- `GET /api/projects` - 项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

#### 文件管理 API
- `GET /api/files` - 文件列表
- `POST /api/files` - 创建文件
- `GET /api/files/{id}` - 文件详情
- `PUT /api/files/{id}` - 更新文件
- `DELETE /api/files/{id}` - 删除文件
- `GET /api/files/{id}/versions` - 版本历史
- `POST /api/files/{id}/restore/{version}` - 恢复版本

#### LLM配置 API
- `GET /api/llm-configs` - 配置列表
- `POST /api/llm-configs` - 创建配置
- `GET /api/llm-configs/{id}` - 配置详情
- `PUT /api/llm-configs/{id}` - 更新配置
- `DELETE /api/llm-configs/{id}` - 删除配置
- `POST /api/llm-configs/{id}/activate` - 激活配置
- `POST /api/llm-configs/{id}/test` - 测试连接
- `GET /api/llm-configs/active` - 获取活跃配置

#### 执行控制 API
- `POST /api/execution/{project_id}/start` - 启动执行
- `POST /api/execution/{project_id}/stop` - 停止执行
- `GET /api/execution/{project_id}/status` - 执行状态
- `GET /api/execution/{project_id}/artifacts` - 获取工件

#### 智能体活动 API
- `GET /api/agent-activities` - 活动列表
- `GET /api/agent-activities/active` - 活跃活动
- `GET /api/agent-activities/{id}` - 活动详情

#### 模板管理 API 🆕
- `GET /api/v1/templates` - 模板列表（支持分类和标签过滤）
- `GET /api/v1/templates/{id}` - 模板详情
- `GET /api/v1/templates/{id}/preview` - 模板预览
- `POST /api/v1/templates/{id}/apply` - 应用模板
- `GET /api/v1/templates/categories/list` - 列出分类

#### 系统 API
- `GET /health` - 健康检查

## 🧪 测试

### 运行测试

```bash
# 运行所有单元测试
PYTHONPATH=src pytest tests/ -v

# 运行特定测试
PYTHONPATH=src pytest tests/test_llm_factory.py -v

# 生成覆盖率报告
PYTHONPATH=src pytest --cov=src/resoftai --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# 运行API集成测试
python tests/test_api_integration.py
```

### 测试统计

- ✅ 单元测试: **52个通过** (核心 + 代码质量 + 模板API)
- ✅ 测试覆盖率: **45%** (从43%提升)
  - 模板系统: 91-100%
  - 代码质量模块: 88%
  - API路由: 完整覆盖
- ✅ API集成测试: 10/10 (100%通过率)
- ✅ API端点: **32个**全部可用
- ✅ 数据库表: 8个创建成功

详见 [TESTING.md](TESTING.md) 获取完整的测试文档。

## 🔧 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | sqlite+aiosqlite:///./resoftai.db |
| JWT_SECRET_KEY | JWT密钥 | (必需) |
| JWT_ALGORITHM | JWT算法 | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 访问令牌过期时间 | 30 |
| JWT_REFRESH_TOKEN_EXPIRE_DAYS | 刷新令牌过期天数 | 7 |
| DEEPSEEK_API_KEY | DeepSeek API密钥 | (可选) |
| ANTHROPIC_API_KEY | Anthropic API密钥 | (可选) |
| CORS_ORIGINS | CORS允许的源 | * |

### LLM提供商支持

- ✅ DeepSeek
- ✅ Anthropic Claude
- ✅ Google Gemini
- ✅ Moonshot AI
- ✅ Zhipu AI
- ✅ MiniMax

## 📊 技术栈

### 后端
- **FastAPI** - 现代Web框架
- **SQLAlchemy** - ORM
- **Alembic** - 数据库迁移
- **Pydantic** - 数据验证
- **Python-Jose** - JWT
- **Passlib** - 密码哈希
- **Python-SocketIO** - WebSocket
- **Uvicorn** - ASGI服务器

### 前端
- **Vue 3** - 前端框架
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Element Plus** - UI组件库
- **Monaco Editor** - 代码编辑器
- **Axios** - HTTP客户端

### 数据库
- **PostgreSQL** - 生产环境
- **SQLite** - 开发/测试环境

### 开发工具
- **pytest** - 测试框架
- **pytest-asyncio** - 异步测试
- **pytest-cov** - 覆盖率报告
- **Black** - 代码格式化
- **Ruff** - 代码检查
- **MyPy** - 类型检查

### DevOps 🆕
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排
- **GitHub Actions** - CI/CD自动化
- **Bandit** - 安全扫描

## 📊 项目状态

当前版本: **0.2.0** (Beta)

### 已完成功能 ✅

- ✅ 核心框架完成
- ✅ 7个专业智能体实现
- ✅ 工作流编排器
- ✅ 项目执行器
- ✅ 数据库模型（8个表）
- ✅ RESTful API（**32个端点**）
- ✅ JWT认证授权
- ✅ 文件版本控制
- ✅ LLM抽象层（6个提供商）
- ✅ WebSocket实时通信
- ✅ Monaco编辑器集成
- ✅ 测试框架（**52+测试用例**）
- ✅ API文档（Swagger/ReDoc）
- ✅ 数据库迁移（Alembic）
- ✅ 启动脚本和文档
- ✅ argon2密码哈希系统 (v0.2.1)
- ✅ 100% API集成测试通过率 (v0.2.1)
- ✅ 代码质量检查系统 (支持9种语言) (v0.2.1)
- ✅ 多语言最佳实践库 (v0.2.1)
- ✅ 增强的Developer代理 (v0.2.1)
- ✅ **项目模板系统** (v0.2.2) 🆕
- ✅ **Docker容器化部署** (v0.2.2) 🆕
- ✅ **CI/CD自动化流程** (v0.2.2) 🆕

### 进行中 ⏳

- ⏳ 前端UI完善（启动Vue开发服务器，测试前后端集成）
- ⏳ 提高单元测试覆盖率到80%+ (当前45%)
- ⏳ 性能优化和负载测试
- ⏳ 前端代码质量报告显示

### 计划中 📋

- 📋 更多项目模板（微服务、数据管道、ML项目等）
- 📋 实时协作功能（多用户编辑、在线状态）
- 📋 集成静态分析工具API接口 (pylint, mypy, eslint)
- 📋 生产环境部署指南
- 📋 更多智能体能力扩展
- 📋 云服务集成（AWS/Azure/GCP）
- 📋 插件系统

## 🗺️ 下一步计划

### 已完成 (v0.2.2) ✅

1. ✅ **项目模板系统** - REST API + WebSocket实时反馈
2. ✅ **CI/CD自动化** - GitHub Actions + Docker容器化
3. ✅ **测试覆盖率提升** - 从43%提升至45%

### 即将完成 (v0.2.3)

1. **前端集成测试** - 启动Vue应用并测试UI
2. **提高测试覆盖率** - 目标60%+ (API Routes, Generator)
3. **静态分析工具API** - pylint, mypy, eslint集成
4. **实时协作功能** - WebSocket多用户编辑

### 中期规划 (v0.3.0)

- 支持更多AI模型（OpenAI GPT, etc.）
- Web前端界面完善
- 更多项目模板（微服务、数据管道、ML项目）
- 实时协作功能完善
- 性能优化和负载测试

### 长期目标 (v1.0.0)

- 多语言支持（国际化）
- 云服务部署（AWS/Azure/GCP）
- 企业版功能
- 私有化部署支持
- 插件系统
- 市场和社区

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 遵循PEP 8（Python）
- 使用Black格式化代码
- 通过Ruff代码检查
- 编写单元测试
- 更新相关文档

## 📄 相关文档

- [测试文档](TESTING.md) - 完整的测试指南
- [快速开始](QUICKSTART.md) - 详细的启动指南
- [开发进度](DEVELOPMENT_PROGRESS.md) - 开发进度报告
- [API文档](http://localhost:8000/docs) - 交互式API文档

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- **softctwo** - [softctwo@aliyun.com](mailto:softctwo@aliyun.com)

## 🙏 致谢

- Anthropic Claude AI
- DeepSeek AI
- Python开源社区
- Vue.js社区
- 所有贡献者

## 📞 联系方式

- 邮箱: softctwo@aliyun.com
- 项目主页: https://github.com/softctwo/resoftai-cli
- 问题反馈: https://github.com/softctwo/resoftai-cli/issues

## ⭐ Star历史

如果这个项目对您有帮助，请给它一个Star ⭐！

---

**注意**: 本项目目前处于Beta阶段，核心功能已完成并测试通过。生产环境使用前请充分测试。
