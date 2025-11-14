# ResoftAI - 企业级多智能体软件开发协作平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![Test Coverage](https://img.shields.io/badge/coverage-90%2B%25-brightgreen.svg)](https://github.com/softctwo/resoftai-cli)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://hub.docker.com/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen.svg)](https://github.com/softctwo/resoftai-cli)

> 🚀 **v0.2.2 "Enterprise Ready"** - 生产级 AI 驱动的软件定制开发服务平台，通过多智能体协作自动化完成从需求到交付的全流程

## 📋 项目简介

ResoftAI 是一个创新的**企业级多智能体协作平台**，专为软件定制开发服务而设计。平台集成了 **7 个专业 AI 智能体**，模拟真实软件开发团队的协作模式，能够自动化完成从需求收集到最终交付的整个软件开发生命周期。

**v0.2.2 版本亮点**：
- ✨ 完整的企业功能（组织、团队、RBAC、配额管理）
- 🎨 全功能插件市场生态系统
- 📱 移动端响应式设计
- 📊 实时性能监控仪表板
- 🚀 一键生产部署基础设施
- 📚 40,000+ 字完整文档

---

## 🌟 核心特性

### 🤖 七大专业 AI 智能体

完整覆盖软件开发生命周期的专业智能体团队：

- **项目经理 (Project Manager)** - 项目规划、进度管理、资源协调
- **需求分析师 (Requirements Analyst)** - 需求收集、SRS 文档生成
- **软件架构师 (Architect)** - 系统设计、架构决策、技术选型
- **UX/UI 设计师 (Designer)** - 界面设计、用户体验优化
- **开发工程师 (Developer)** - 代码实现、质量检查（支持 9 种语言）
- **测试工程师 (Test Engineer)** - 测试用例设计、自动化测试
- **质量专家 (QA Expert)** - 代码审查、质量保证、最终验收

### 🏢 企业级功能 (v0.2.2 新增)

完整的多租户企业管理系统：

#### 组织管理
- **多组织支持** - 完整的数据隔离
- **四级层级体系** - FREE, STARTER, PROFESSIONAL, ENTERPRISE
- **SSO/SAML 集成** - 企业身份认证
- **自定义品牌** - 组织级配置

#### 团队协作
- **灵活团队结构** - 组织内多团队管理
- **角色权限控制 (RBAC)** - OWNER, ADMIN, MEMBER, VIEWER
- **项目分配** - 团队级项目管理
- **成员邀请** - 完整的邀请工作流

#### 配额管理
- **五种配额类型**：
  - 项目数量限制
  - API 调用限制
  - 存储空间限制
  - 团队成员数量
  - LLM Token 使用量
- **实时使用追踪** - 可视化进度条
- **自动告警** - 80%, 90%, 100% 阈值提醒
- **层级限制** - 基于订阅层级的配额

#### 审计日志
- 完整的用户活动追踪
- 安全事件记录
- 合规性报告
- 数据导出功能

### 🔌 插件市场生态 (v0.2.2 新增)

完整的插件系统和市场平台：

- **插件发现** - 搜索、分类、标签过滤
- **精选推荐** - 热门插件、编辑推荐
- **版本管理** - 兼容性检查、自动更新
- **评分评论** - 用户反馈系统
- **一键安装** - 自动依赖解析
- **插件管理** - 激活/停用、配置管理
- **Hook 系统** - 事件驱动的扩展机制

### 📱 移动响应式设计 (v0.2.2 新增)

移动优先的完整响应式系统：

- **五个断点** - xs(480px), sm(768px), md(992px), lg(1200px), xl(1600px)
- **触摸优化** - 移动端友好的交互
- **响应式导航** - 侧边栏滑出、汉堡菜单
- **自适应布局** - 所有屏幕尺寸完美适配
- **Vue 3 组合函数** - `useResponsive()` 响应式工具
- **SCSS 混合库** - 50+ 响应式工具类

### 📊 性能监控仪表板 (v0.2.2 新增)

实时性能追踪和分析系统：

- **系统指标** - CPU, 内存, 磁盘, 网络
- **智能体性能** - 执行时间、成功率、错误率
- **LLM 性能** - Token 使用、响应时间、成本分析
- **工作流指标** - 阶段耗时、瓶颈识别
- **实时图表** - Chart.js 集成
- **历史趋势** - 可配置时间范围

### 🚀 生产部署基础设施 (v0.2.2 新增)

完整的生产级部署解决方案：

#### 一键部署
- **自动化脚本** - `deploy_production.sh` 完整部署
- **数据库设置** - PostgreSQL 自动配置
- **SSL 证书** - Let's Encrypt 自动续期
- **环境配置** - 100+ 配置项模板

#### 安全加固
- **HTTPS 强制** - 自动 HTTP 重定向
- **安全头** - HSTS, CSP, X-Frame-Options
- **速率限制** - API, 认证, 文件上传
- **防火墙** - UFW 自动配置
- **入侵防护** - Fail2Ban 集成

#### 监控日志
- **Systemd 服务** - 自动重启
- **日志轮转** - 14 天保留
- **Prometheus 集成** - 可选监控
- **Sentry 集成** - 错误追踪

#### 备份恢复
- **自动备份** - 每日数据库备份
- **文件备份** - 每周文件备份
- **S3 支持** - 远程备份存储
- **恢复测试** - 备份验证

### 📊 完整的工作流引擎

7 阶段工作流编排系统：

```
需求分析 → 架构设计 → UI 设计 → 开发 → 测试 → QA 审核 → 完成
```

- **智能编排** - 自动任务调度
- **实时追踪** - WebSocket 进度推送
- **状态持久化** - 完整的状态管理
- **错误恢复** - 自动重试机制
- **迭代支持** - 阶段跳过和回退

### 💾 强大的数据管理

- **双数据库支持** - SQLite 开发 / PostgreSQL 生产
- **27 个数据模型** - 包括 19 个企业表
- **完整版本控制** - 项目和文件历史
- **智能体追踪** - 活动日志记录
- **异步 ORM** - SQLAlchemy 2.0
- **数据库迁移** - Alembic 完整支持

### 🎯 多种交互方式

- **70+ REST API** - 完整的 API 端点
- **Vue 3 前端** - 现代化管理界面
- **Monaco 编辑器** - 代码编辑集成
- **WebSocket** - 实时双向通信
- **OpenAPI 文档** - Swagger/ReDoc

### 📦 项目模板系统

- **3 个内置模板** - FastAPI REST API, React+FastAPI Web App, Python CLI Tool
- **变量系统** - 类型验证、默认值、必填项
- **模板预览** - 应用前预览
- **实时反馈** - WebSocket 进度推送
- **多种过滤** - 分类、标签筛选

### ✨ 代码质量保证

- **9 种编程语言** - Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP
- **安全检测** - SQL 注入, XSS, 硬编码密码
- **最佳实践** - 代码规范、命名约定
- **质量评分** - 0-100 分自动评分
- **迭代优化** - 自动代码改进

---

## 🏗️ 系统架构

### 目录结构

```
resoftai-cli/
├── src/resoftai/              # 后端源代码
│   ├── core/                  # 核心组件
│   │   ├── agent.py          # 智能体基类
│   │   ├── workflow.py       # 工作流引擎
│   │   ├── message_bus.py    # 消息总线
│   │   └── state.py          # 状态管理
│   ├── agents/                # 7 个专业智能体
│   ├── orchestration/        # 工作流编排
│   ├── api/                   # FastAPI 应用
│   │   └── routes/           # 70+ API 路由
│   ├── models/                # 27 个数据模型
│   │   ├── enterprise.py     # 企业功能模型 (19 表)
│   │   └── ...
│   ├── crud/                  # 数据库操作层
│   │   ├── enterprise.py     # 企业 CRUD
│   │   └── ...
│   ├── plugins/               # 插件系统 🆕
│   │   ├── manager.py        # 插件管理器
│   │   ├── hooks.py          # Hook 系统
│   │   └── base.py           # 插件基类
│   ├── monitoring/            # 性能监控 🆕
│   ├── llm/                   # LLM 抽象层 (6 提供商)
│   ├── auth/                  # JWT 认证授权
│   └── websocket/             # WebSocket 管理
│
├── frontend/                  # Vue 3 前端 🆕
│   ├── src/
│   │   ├── components/       # 公共组件
│   │   ├── views/            # 页面组件
│   │   │   ├── PluginMarketplace.vue      # 插件市场
│   │   │   ├── PluginDetail.vue           # 插件详情
│   │   │   ├── InstalledPlugins.vue       # 已安装插件
│   │   │   ├── OrganizationManagement.vue # 组织管理
│   │   │   ├── TeamManagement.vue         # 团队管理
│   │   │   ├── QuotaMonitoring.vue        # 配额监控
│   │   │   └── PerformanceMonitoring.vue  # 性能监控
│   │   ├── composables/      # Vue 组合函数
│   │   │   └── useResponsive.js  # 响应式工具
│   │   ├── styles/           # 样式文件
│   │   │   └── responsive.scss   # 响应式 SCSS
│   │   └── utils/            # 工具函数
│   │       └── api.js        # API 客户端
│   └── package.json
│
├── scripts/                   # 部署和工具脚本
│   ├── deploy_production.sh  # 一键部署 🆕
│   ├── setup_production_db.sh # 数据库设置 🆕
│   ├── setup_ssl.sh          # SSL 证书 🆕
│   └── init_db.py            # 数据库初始化
│
├── tests/                     # 测试套件 (90%+ 覆盖率)
│   ├── performance/          # 性能测试 🆕
│   │   └── loadtest.py       # Locust 负载测试
│   ├── enterprise/           # 企业功能测试
│   ├── plugins/              # 插件系统测试
│   └── api/                  # API 测试
│
├── docs/                      # 完整文档 (40,000+ 字) 🆕
│   ├── USER_MANUAL.md        # 用户手册 (15,000 字)
│   ├── API_DOCUMENTATION.md  # API 文档 (10,000 字)
│   ├── DEPLOYMENT_CHECKLIST.md # 部署清单 (801 行)
│   ├── MOBILE_OPTIMIZATION.md  # 移动优化指南
│   └── ENTERPRISE.md         # 企业功能文档
│
├── alembic/                   # 数据库迁移
├── .env.production.example    # 生产环境配置模板 🆕
├── docker-compose.yml         # Docker 编排
├── Dockerfile                 # Docker 镜像
└── RELEASE_NOTES_v0.2.2.md   # 发布说明 🆕
```

### 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端层 (Client)                       │
├─────────────────────────────────────────────────────────────┤
│  Vue 3 前端  │  移动端  │  REST API 客户端  │  CLI 工具    │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API 网关层 (Nginx + FastAPI)               │
├─────────────────────────────────────────────────────────────┤
│  认证授权  │  速率限制  │  CORS  │  SSL/TLS  │  日志      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Application)                    │
├─────────────────────────────────────────────────────────────┤
│  70+ API 端点  │  WebSocket 服务  │  业务逻辑处理          │
│  企业功能  │  插件系统  │  性能监控  │  配额管理            │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   智能体编排层 (Orchestration)               │
├─────────────────────────────────────────────────────────────┤
│  工作流引擎  │  7 个 AI 智能体  │  消息总线  │  状态管理  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data)                           │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (27 表)  │  Redis (缓存)  │  文件存储           │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  外部服务层 (External Services)              │
├─────────────────────────────────────────────────────────────┤
│  DeepSeek/Claude/Gemini  │  Prometheus  │  Sentry  │  S3   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 📋 环境要求

#### 最小配置（开发环境）
- **操作系统**: Ubuntu 22.04 LTS / macOS / Windows 10+
- **Python**: 3.11 或更高版本
- **Node.js**: 20.x (前端开发)
- **数据库**: SQLite (自动) 或 PostgreSQL 14+
- **内存**: 4 GB RAM
- **磁盘**: 10 GB 可用空间

#### 推荐配置（生产环境）
- **操作系统**: Ubuntu 22.04 LTS
- **Python**: 3.11+
- **Node.js**: 20.x
- **数据库**: PostgreSQL 14+
- **Redis**: 6+
- **CPU**: 4 vCPU
- **内存**: 8 GB RAM
- **磁盘**: 100 GB SSD

### 🐳 Docker Compose 快速启动 (推荐)

**最简单的方式 - 一键启动完整环境**：

```bash
# 1. 克隆仓库
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 2. 配置环境变量
cp .env.production.example .env
nano .env  # 配置 LLM API 密钥

# 3. 一键启动
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 访问服务
# Backend API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 💻 本地开发环境设置

#### 1. 克隆仓库

```bash
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli
```

#### 2. 后端设置

```bash
# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.production.example .env
nano .env  # 编辑配置
```

**最小环境变量配置**：

```bash
# 数据库 (SQLite 开发模式)
DATABASE_URL=sqlite+aiosqlite:///./resoftai.db

# JWT 配置
JWT_SECRET_KEY=your-random-secret-key-here-change-this
JWT_ALGORITHM=HS256

# LLM 配置 (至少配置一个)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
# 或
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
```

#### 3. 初始化数据库

```bash
# 运行数据库初始化脚本
python scripts/init_db.py

# 或运行迁移 (推荐)
export PYTHONPATH=src
alembic upgrade head
```

#### 4. 启动后端服务

```bash
# 开发模式 (自动重载)
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload --port 8000

# 或使用脚本
bash scripts/start_backend.sh
```

#### 5. 启动前端 (可选)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### ✅ 验证安装

```bash
# 1. 健康检查
curl http://localhost:8000/api/v1/health
# 输出: {"status":"healthy","service":"resoftai-api","version":"0.2.2"}

# 2. 访问 API 文档
open http://localhost:8000/docs  # macOS
# 或 xdg-open http://localhost:8000/docs  # Linux

# 3. 运行测试
PYTHONPATH=src pytest tests/ -v

# 4. 检查测试覆盖率
PYTHONPATH=src pytest --cov=src/resoftai --cov-report=html
open htmlcov/index.html
```

---

## 🚀 生产环境部署

### 一键部署脚本

ResoftAI 提供完整的一键部署解决方案：

```bash
# 准备服务器 (Ubuntu 22.04 LTS)
# 最小配置: 2 vCPU, 4 GB RAM, 50 GB SSD

# 1. 克隆代码
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 2. 一键部署 (包括数据库、SSL、Nginx、服务配置)
sudo bash scripts/deploy_production.sh yourdomain.com

# 3. 配置环境变量
sudo nano /opt/resoftai/.env
# 配置 LLM API 密钥和其他设置

# 4. 重启服务
sudo systemctl restart resoftai

# 5. 访问系统
# https://yourdomain.com
# 默认管理员: admin / admin123 (请立即更改!)
```

### 分步部署

#### 1. 数据库设置

```bash
# 自动安装和配置 PostgreSQL
sudo bash scripts/setup_production_db.sh
```

#### 2. SSL 证书

```bash
# Let's Encrypt 自动配置
sudo bash scripts/setup_ssl.sh yourdomain.com
```

#### 3. 完整部署

详见完整的部署文档：

- **部署清单**: `docs/DEPLOYMENT_CHECKLIST.md` (50+ 检查项)
- **用户手册**: `docs/USER_MANUAL.md` (15,000+ 字)
- **API 文档**: `docs/API_DOCUMENTATION.md` (10,000+ 字)

---

## 📖 使用指南

### 快速体验

#### 1. 注册用户

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "SecurePass123"
  }'
```

#### 2. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "SecurePass123"
  }'

# 保存返回的 access_token
TOKEN="your-access-token-here"
```

#### 3. 创建项目

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "任务管理系统",
    "description": "一个现代化的任务管理 Web 应用",
    "requirements": "开发支持用户注册、任务创建、分配和追踪的系统",
    "language": "python",
    "framework": "fastapi"
  }'
```

#### 4. 启动项目执行

```bash
curl -X POST "http://localhost:8000/api/v1/projects/{project_id}/execute" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. 查看执行状态

```bash
curl "http://localhost:8000/api/v1/projects/{project_id}/status" \
  -H "Authorization: Bearer $TOKEN"
```

### 企业功能使用

#### 创建组织

```bash
curl -X POST "http://localhost:8000/api/v1/organizations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的公司",
    "description": "企业组织",
    "tier": "PROFESSIONAL"
  }'
```

#### 创建团队

```bash
curl -X POST "http://localhost:8000/api/v1/teams" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": 1,
    "name": "开发团队",
    "description": "核心开发团队"
  }'
```

#### 查看配额使用情况

```bash
curl "http://localhost:8000/api/v1/quotas/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 插件市场使用

#### 浏览插件

```bash
# 列出所有插件
curl "http://localhost:8000/api/v1/plugins/marketplace" \
  -H "Authorization: Bearer $TOKEN"

# 搜索插件
curl "http://localhost:8000/api/v1/plugins/marketplace/search?q=test" \
  -H "Authorization: Bearer $TOKEN"
```

#### 安装插件

```bash
curl -X POST "http://localhost:8000/api/v1/plugins/install" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "pytest-plugin",
    "version": "1.0.0"
  }'
```

---

## 📚 API 文档

### API 概览

ResoftAI 提供 **70+ REST API 端点**，完整覆盖所有功能模块。

访问 **[http://localhost:8000/docs](http://localhost:8000/docs)** 查看完整的交互式 API 文档（Swagger UI）。

### 主要 API 模块

#### 🔐 认证 API (5 个端点)
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新令牌
- `GET /api/v1/auth/me` - 获取当前用户

#### 📁 项目管理 API (10 个端点)
- `GET /api/v1/projects` - 项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/{id}` - 项目详情
- `PUT /api/v1/projects/{id}` - 更新项目
- `DELETE /api/v1/projects/{id}` - 删除项目
- `POST /api/v1/projects/{id}/execute` - 执行项目
- `GET /api/v1/projects/{id}/status` - 执行状态
- `GET /api/v1/projects/{id}/files` - 项目文件
- 等...

#### 🏢 企业功能 API (20+ 个端点)
- **组织管理** (8 个端点)
- **团队管理** (8 个端点)
- **配额管理** (5 个端点)

#### 🔌 插件系统 API (15 个端点)
- 插件市场浏览
- 插件安装/卸载
- 插件配置管理
- 插件评分评论

#### 📊 性能监控 API (5 个端点)
- 系统指标
- 智能体性能
- LLM 性能
- 工作流指标

#### 📦 模板系统 API (5 个端点)
- 模板列表
- 模板详情
- 模板应用
- 模板预览

完整 API 文档请查看：`docs/API_DOCUMENTATION.md` (10,000+ 字)

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
PYTHONPATH=src pytest tests/ -v

# 运行特定模块测试
PYTHONPATH=src pytest tests/test_workflow.py -v

# 生成覆盖率报告
PYTHONPATH=src pytest --cov=src/resoftai --cov-report=html --cov-report=term

# 查看覆盖率报告
open htmlcov/index.html
```

### 负载测试

```bash
# 安装 Locust
pip install locust faker

# 运行负载测试 (Web UI)
locust -f tests/performance/loadtest.py --host=http://localhost:8000

# 无头模式运行
locust -f tests/performance/loadtest.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless
```

### 测试统计

- ✅ **测试覆盖率**: **90%+** (从 43% 大幅提升)
- ✅ **单元测试**: 100+ 测试用例
- ✅ **集成测试**: 完整 API 测试
- ✅ **企业功能测试**: 完整覆盖
- ✅ **插件系统测试**: 完整覆盖
- ✅ **性能测试**: Locust 负载测试套件

---

## 📊 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.11+ | 编程语言 |
| **FastAPI** | 0.104+ | Web 框架 |
| **SQLAlchemy** | 2.0 | 异步 ORM |
| **Alembic** | - | 数据库迁移 |
| **Pydantic** | 2.x | 数据验证 |
| **PostgreSQL** | 14+ | 生产数据库 |
| **Redis** | 6+ | 缓存和会话 |
| **Uvicorn** | - | ASGI 服务器 |
| **Gunicorn** | - | 进程管理 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue** | 3.x | 前端框架 |
| **Element Plus** | - | UI 组件库 |
| **Vite** | 5.x | 构建工具 |
| **Chart.js** | 4.x | 图表库 |
| **Axios** | 1.x | HTTP 客户端 |
| **Monaco Editor** | - | 代码编辑器 |

### DevOps 和部署

| 技术 | 用途 |
|------|------|
| **Docker** | 容器化 |
| **Docker Compose** | 服务编排 |
| **Nginx** | 反向代理 |
| **Let's Encrypt** | SSL 证书 |
| **Systemd** | 服务管理 |
| **UFW** | 防火墙 |
| **Fail2Ban** | 入侵防护 |
| **Prometheus** | 监控指标 |
| **Sentry** | 错误追踪 |

### AI 和 LLM

支持的 LLM 提供商：

- ✅ **DeepSeek** (推荐)
- ✅ **Anthropic Claude**
- ✅ **Google Gemini**
- ✅ **Moonshot AI**
- ✅ **Zhipu AI**
- ✅ **MiniMax**

---

## 📊 项目状态

### 当前版本

**v0.2.2 (Beta)** - "Enterprise Ready" - 2025-11-14

### 已完成功能 ✅

#### 核心功能
- ✅ 7 个专业 AI 智能体
- ✅ 完整工作流编排系统
- ✅ 70+ REST API 端点
- ✅ 27 个数据库表 (含 19 个企业表)
- ✅ JWT 认证授权
- ✅ WebSocket 实时通信
- ✅ 6 个 LLM 提供商支持

#### 企业功能 (v0.2.2)
- ✅ 组织管理系统
- ✅ 团队协作功能
- ✅ 角色权限控制 (RBAC)
- ✅ 配额管理系统
- ✅ 审计日志记录
- ✅ SSO/SAML 支持

#### 插件生态 (v0.2.2)
- ✅ 插件市场完整前端
- ✅ 插件管理系统
- ✅ Hook 事件系统
- ✅ 插件评分评论

#### 前端界面 (v0.2.2)
- ✅ 移动响应式设计
- ✅ 插件市场界面 (3 个组件)
- ✅ 企业管理界面 (3 个组件)
- ✅ 性能监控仪表板
- ✅ 代码编辑器集成

#### 部署基础设施 (v0.2.2)
- ✅ 一键部署脚本
- ✅ 数据库自动配置
- ✅ SSL 证书自动化
- ✅ 生产环境模板
- ✅ 负载测试套件

#### 文档 (v0.2.2)
- ✅ 用户手册 (15,000+ 字)
- ✅ API 文档 (10,000+ 字)
- ✅ 部署清单 (801 行)
- ✅ 移动优化指南
- ✅ 发布说明

### 统计数据

- **代码行数**: 15,000+ 行新增代码
- **文档字数**: 40,000+ 字
- **API 端点**: 70+ 个
- **测试覆盖率**: 90%+
- **数据库表**: 27 个
- **前端组件**: 15+ 个

---

## 🗺️ 开发路线图

### v0.3.0 (计划中 - 1-2 个月)

#### 功能增强
- [ ] 实时协作编辑增强
- [ ] 工作流可视化编辑器
- [ ] 高级代码分析功能
- [ ] 智能代码审查

#### 集成扩展
- [ ] GitHub/GitLab 深度集成
- [ ] Jira/Linear 项目管理
- [ ] Slack/Teams 通知
- [ ] 更多 LLM 提供商

#### 性能优化
- [ ] 数据库查询优化
- [ ] Redis 缓存策略
- [ ] 异步任务队列
- [ ] CDN 集成

### v0.4.0 (计划中 - 2-3 个月)

- [ ] Kubernetes 部署支持
- [ ] Helm Charts
- [ ] 服务网格集成
- [ ] 自动伸缩
- [ ] 多区域部署

### v1.0.0 (长期目标 - 3-6 个月)

- [ ] 云原生架构
- [ ] 多语言国际化
- [ ] 插件市场平台
- [ ] 开发者社区
- [ ] 企业级 SLA

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork 本仓库**
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'feat: Add some AmazingFeature'`)
4. **推送到分支** (`git push origin feature/AmazingFeature`)
5. **创建 Pull Request**

### 代码规范

- 遵循 **PEP 8** (Python)
- 使用 **Black** 格式化代码
- 通过 **Ruff** 代码检查
- 通过 **MyPy** 类型检查
- **编写单元测试**
- **更新相关文档**

### 提交规范

使用语义化提交信息：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具

---

## 📄 相关文档

### 核心文档

- **[用户手册](docs/USER_MANUAL.md)** - 完整的用户指南 (15,000+ 字)
- **[API 文档](docs/API_DOCUMENTATION.md)** - API 参考手册 (10,000+ 字)
- **[部署清单](docs/DEPLOYMENT_CHECKLIST.md)** - 生产部署指南 (801 行)
- **[发布说明](RELEASE_NOTES_v0.2.2.md)** - v0.2.2 发布详情

### 专题文档

- **[移动优化](docs/MOBILE_OPTIMIZATION.md)** - 响应式设计指南
- **[企业功能](docs/ENTERPRISE.md)** - 企业版功能说明
- **[测试文档](docs/TEST_COVERAGE_IMPROVEMENTS.md)** - 测试策略

### 在线文档

- **[Swagger UI](http://localhost:8000/docs)** - 交互式 API 文档
- **[ReDoc](http://localhost:8000/redoc)** - API 文档阅读版

---

## 📞 支持和联系

### 获取帮助

- **📧 邮箱**: softctwo@aliyun.com
- **🐛 问题反馈**: [GitHub Issues](https://github.com/softctwo/resoftai-cli/issues)
- **📖 文档**: `docs/` 目录
- **💬 讨论**: [GitHub Discussions](https://github.com/softctwo/resoftai-cli/discussions)

### 社区

- **GitHub**: https://github.com/softctwo/resoftai-cli
- **Star** ⭐ 本项目，关注最新动态

---

## 📄 许可证

本项目采用 **MIT 许可证** - 详见 [LICENSE](LICENSE) 文件

---

## 👥 作者和贡献者

### 主要作者

- **softctwo** - 项目创始人和主要开发者
- 邮箱: softctwo@aliyun.com

### 致谢

特别感谢：

- **Anthropic Claude AI** - AI 开发辅助
- **DeepSeek AI** - LLM 服务支持
- **Python 开源社区**
- **Vue.js 生态系统**
- **所有贡献者和用户**

---

## ⭐ Star 历史

如果这个项目对您有帮助，请给它一个 **Star** ⭐！

[![Star History Chart](https://api.star-history.com/svg?repos=softctwo/resoftai-cli&type=Date)](https://star-history.com/#softctwo/resoftai-cli&Date)

---

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/softctwo/resoftai-cli?style=social)
![GitHub forks](https://img.shields.io/github/forks/softctwo/resoftai-cli?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/softctwo/resoftai-cli?style=social)

---

## 🎉 快速链接

- 🚀 [快速开始](#-快速开始)
- 📖 [使用指南](#-使用指南)
- 🚀 [生产部署](#-生产环境部署)
- 📚 [API 文档](#-api-文档)
- 🗺️ [路线图](#-开发路线图)
- 🤝 [贡献指南](#-贡献指南)

---

<div align="center">

**ResoftAI v0.2.2 - Building the Future of AI-Powered Software Development** 🚀

现在就开始使用 ResoftAI，体验 AI 驱动的软件开发革命！

[开始使用](https://github.com/softctwo/resoftai-cli) • [查看文档](docs/) • [报告问题](https://github.com/softctwo/resoftai-cli/issues)

</div>

---

**注意**: 本项目目前处于 **Beta** 阶段。核心功能已完成并经过充分测试（90%+ 测试覆盖率），可用于生产环境。使用前请参考完整的[部署清单](docs/DEPLOYMENT_CHECKLIST.md)。
