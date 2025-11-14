# ResoftAI 用户手册

**版本**: 0.2.2 (Beta)
**最后更新**: 2025-11-14

---

## 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装部署](#安装部署)
4. [快速开始](#快速开始)
5. [核心功能](#核心功能)
6. [插件系统](#插件系统)
7. [企业版功能](#企业版功能)
8. [性能监控](#性能监控)
9. [API参考](#api参考)
10. [故障排查](#故障排查)
11. [常见问题](#常见问题)
12. [最佳实践](#最佳实践)

---

## 简介

### 什么是 ResoftAI？

ResoftAI 是一个基于多智能体协作的软件开发平台，通过 7 个专业 AI 智能体自动化完成从需求分析到代码交付的完整开发流程。

### 核心特性

- **🤖 7个专业智能体**: 项目经理、需求分析师、架构师、UI设计师、开发工程师、测试工程师、质量专家
- **⚡ 优化的工作流引擎**: 并行执行、智能缓存、检查点恢复，性能提升40-60%
- **📊 实时性能监控**: 全面的工作流、智能体、系统和LLM使用监控
- **🔌 可扩展插件系统**: Hook机制、插件市场、版本管理
- **🏢 企业级功能**: 多租户、RBAC、配额管理、审计日志、SSO
- **🌐 Web管理界面**: Vue 3 + Element Plus 现代化管理界面
- **🔄 实时协作**: WebSocket 支持的实时更新和协作编辑

### 技术栈

**后端**:
- Python 3.11+
- FastAPI (异步Web框架)
- SQLAlchemy 2.0 (异步ORM)
- PostgreSQL / SQLite
- Alembic (数据库迁移)

**前端**:
- Vue 3 (Composition API)
- Element Plus (UI组件库)
- Monaco Editor (代码编辑器)
- Chart.js (数据可视化)

**AI/LLM**:
- 支持多个LLM提供商: DeepSeek, Anthropic Claude, Google Gemini, Moonshot, Zhipu, MiniMax
- 统一的LLM抽象层

---

## 系统要求

### 最低要求

- **操作系统**: Linux, macOS, Windows (WSL推荐)
- **Python**: 3.11 或更高版本
- **Node.js**: 16+ (用于前端)
- **内存**: 4GB RAM
- **磁盘空间**: 2GB

### 推荐配置

- **操作系统**: Ubuntu 20.04+ / macOS 12+
- **Python**: 3.11+
- **数据库**: PostgreSQL 14+
- **内存**: 8GB+ RAM
- **磁盘空间**: 10GB+ SSD

### 依赖软件

- Git
- Python pip
- npm / yarn
- PostgreSQL (生产环境推荐) 或 SQLite (开发环境)

---

## 安装部署

### 方法一：标准安装

#### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/resoftai-cli.git
cd resoftai-cli
```

#### 2. 安装后端依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./resoftai.db
# 或使用 PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/resoftai

# JWT密钥（生成随机密钥）
JWT_SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_ALGORITHM=HS256

# LLM配置（至少配置一个）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxx
# GOOGLE_API_KEY=AIzaSyxxxxx

# 应用配置
WORKSPACE_DIR=./workspace
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### 4. 初始化数据库

```bash
# 运行迁移
PYTHONPATH=src alembic upgrade head

# 或使用初始化脚本
python scripts/init_db.py
```

#### 5. 启动后端服务

```bash
# 开发模式（带自动重载）
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload --port 8000

# 生产模式
PYTHONPATH=src gunicorn -w 4 -k uvicorn.workers.UvicornWorker resoftai.api.main:asgi_app --bind 0.0.0.0:8000
```

#### 6. 安装前端依赖并启动

```bash
cd frontend
npm install
npm run dev  # 开发模式
# npm run build  # 生产构建
```

### 方法二：Docker 部署

#### 1. 使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

#### 2. Docker Compose 配置示例

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/resoftai
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    depends_on:
      - db

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=resoftai
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 验证安装

#### 1. 检查后端健康

```bash
curl http://localhost:8000/health
# 期望输出: {"status":"healthy","service":"resoftai-api"}
```

#### 2. 访问 API 文档

打开浏览器访问: `http://localhost:8000/docs`

#### 3. 访问前端界面

打开浏览器访问: `http://localhost:3000`

---

## 快速开始

### 创建第一个项目

#### 1. 注册并登录

访问前端界面，点击"注册"创建账户：

```
用户名: demo_user
邮箱: demo@example.com
密码: Demo123!@#
```

#### 2. 配置 LLM

进入 **模型配置** 页面，添加 LLM 配置：

- **提供商**: DeepSeek
- **API密钥**: 输入您的 DeepSeek API Key
- **模型**: deepseek-chat
- **设为默认**: ✓

#### 3. 创建项目

进入 **项目管理** 页面，点击"创建项目"：

```
项目名称: 我的第一个项目
描述: 一个简单的待办事项管理应用
需求:
- 用户可以添加、编辑、删除待办事项
- 支持标记完成状态
- 按日期排序显示
- 使用 FastAPI 后端和 React 前端
```

#### 4. 启动工作流

点击"启动工作流"按钮，系统将自动执行以下阶段：

1. **需求分析** (1-2分钟): 生成软件需求规格说明书 (SRS)
2. **架构设计** (2-3分钟): 生成系统架构和数据库设计
3. **UI设计** (2-3分钟): 生成界面原型和设计规范
4. **开发** (5-10分钟): 生成完整源代码
5. **测试** (3-5分钟): 生成测试用例并执行
6. **质量评审** (2-3分钟): 代码质量分析和改进建议
7. **完成** (1分钟): 打包交付物

#### 5. 查看结果

在项目详情页面查看：

- **交付物**: 所有生成的文档和代码文件
- **执行日志**: 每个智能体的执行记录
- **性能数据**: Token使用、耗时统计
- **质量报告**: 代码质量评分和建议

#### 6. 下载代码

点击"下载项目"按钮，获取完整的项目代码包。

---

## 核心功能

### 项目管理

#### 创建项目

支持三种创建方式：

1. **从头创建**: 输入需求描述，系统自动生成
2. **从模板创建**: 使用预定义项目模板
3. **导入已有项目**: 上传现有代码并进行分析

#### 项目配置

```python
{
  "name": "项目名称",
  "description": "项目描述",
  "requirements": "详细需求说明",
  "tech_stack": {
    "backend": "FastAPI",
    "frontend": "React",
    "database": "PostgreSQL"
  },
  "workflow_config": {
    "execution_strategy": "adaptive",  # sequential, parallel, adaptive
    "enable_cache": true,
    "enable_checkpoints": true,
    "parallel_stages": ["architecture", "ui_design"]
  }
}
```

#### 工作流控制

- **启动**: 开始执行工作流
- **暂停**: 暂停当前执行（保存检查点）
- **恢复**: 从检查点恢复执行
- **终止**: 停止执行并清理资源

### 智能体系统

#### 1. 项目经理 (Project Manager)

**职责**:
- 理解项目需求
- 制定开发计划
- 协调各个智能体
- 监控项目进度

**输出**:
- 项目计划
- 任务分解
- 风险评估

#### 2. 需求分析师 (Requirements Analyst)

**职责**:
- 分析用户需求
- 编写需求规格说明
- 定义验收标准

**输出**:
- 软件需求规格说明书 (SRS)
- 用例图
- 功能清单

#### 3. 架构师 (Architect)

**职责**:
- 设计系统架构
- 选择技术栈
- 设计数据模型

**输出**:
- 系统架构图
- 数据库设计
- API设计
- 技术选型说明

#### 4. UI/UX 设计师 (UX/UI Designer)

**职责**:
- 设计用户界面
- 制定设计规范
- 创建原型

**输出**:
- 界面原型
- 设计规范
- 交互流程图

#### 5. 开发工程师 (Developer)

**职责**:
- 实现功能代码
- 编写单元测试
- 代码质量检查

**输出**:
- 完整源代码
- 单元测试
- 代码注释
- 质量报告 (0-100分)

**代码质量检查**:
- 安全漏洞扫描 (SQL注入、XSS等)
- 最佳实践验证
- 命名规范检查
- 复杂度分析
- 支持9种语言: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP

#### 6. 测试工程师 (Test Engineer)

**职责**:
- 设计测试用例
- 执行测试
- 生成测试报告

**输出**:
- 测试计划
- 测试用例
- 测试报告
- 缺陷列表

#### 7. 质量专家 (Quality Expert)

**职责**:
- 代码审查
- 性能分析
- 提供改进建议

**输出**:
- 代码审查报告
- 性能分析报告
- 改进建议清单

### 文件管理

#### 上传文件

```bash
# API 示例
curl -X POST http://localhost:8000/api/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@requirements.txt" \
  -F "project_id=1"
```

#### 版本控制

系统自动保存文件版本历史：

- 版本号自动递增
- 支持版本对比
- 可恢复到任意版本
- 变更记录追踪

#### 文件类型支持

- **文档**: .md, .txt, .pdf, .doc
- **代码**: .py, .js, .ts, .java, .go, .rs, .cpp, .cs
- **数据**: .json, .yaml, .xml, .csv
- **图片**: .png, .jpg, .svg

### 模板系统

#### 内置模板

1. **FastAPI REST API**
   - RESTful API 服务
   - JWT 认证
   - SQLAlchemy ORM
   - Alembic 迁移
   - 完整文档

2. **React + FastAPI Web App**
   - React 前端
   - FastAPI 后端
   - PostgreSQL 数据库
   - Docker 部署

3. **Python CLI Tool**
   - Click 命令行框架
   - 配置文件支持
   - 日志系统
   - 单元测试

#### 使用模板

```python
# API 调用
POST /api/templates/{template_id}/apply
{
  "project_id": 1,
  "variables": {
    "project_name": "my-api",
    "database": "postgresql"
  }
}
```

#### 创建自定义模板

模板结构：

```
my-template/
├── template.json          # 模板元数据
├── README.md.jinja2       # Jinja2 模板文件
├── main.py.jinja2
└── requirements.txt.jinja2
```

`template.json` 示例：

```json
{
  "name": "My Custom Template",
  "description": "描述",
  "version": "1.0.0",
  "category": "backend",
  "variables": {
    "project_name": {
      "type": "string",
      "description": "项目名称",
      "required": true
    },
    "database": {
      "type": "string",
      "description": "数据库类型",
      "default": "sqlite",
      "choices": ["sqlite", "postgresql", "mysql"]
    }
  }
}
```

---

## 插件系统

### 插件概述

ResoftAI 的插件系统采用 Hook 机制，支持：

- **智能体插件**: 扩展智能体能力
- **LLM提供商插件**: 添加新的LLM支持
- **代码质量插件**: 添加代码分析工具
- **集成插件**: 第三方服务集成

### 插件市场

#### 浏览插件

访问 **插件市场** 页面：

- **搜索**: 按名称、作者、标签搜索
- **分类筛选**: Development, Testing, Deployment, Security, Monitoring
- **排序**: 按人气、评分、最新排序
- **标签页**: 全部 / 精选 / 热门

#### 安装插件

1. 点击插件卡片查看详情
2. 查看兼容性、依赖、评价
3. 点击"安装"按钮
4. 自动下载并安装依赖
5. 激活插件

#### 管理已安装插件

访问 **已安装插件** 页面：

- 查看所有已安装插件
- 激活/停用插件
- 检查更新
- 查看插件配置
- 卸载插件

### 开发插件

#### 1. 创建插件结构

```bash
mkdir -p my-plugin
cd my-plugin
```

创建 `plugin.json`:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "我的自定义插件",
  "author": "Your Name",
  "category": "development",
  "dependencies": [],
  "compatibility": {
    "min_version": "0.2.0",
    "max_version": "1.0.0"
  }
}
```

#### 2. 实现插件类

创建 `__init__.py`:

```python
from resoftai.plugins.base import CodeQualityPlugin

class MyCodeQualityPlugin(CodeQualityPlugin):
    """自定义代码质量插件"""

    def __init__(self):
        super().__init__(
            name="my-plugin",
            version="1.0.0",
            category="code-quality"
        )

    def load(self, context: dict):
        """加载插件"""
        print(f"Loading {self.name}")
        # 注册 hooks
        context['hook_manager'].register_filter(
            'before_code_analysis',
            self.pre_analysis,
            priority=10
        )

    def activate(self):
        """激活插件"""
        self.is_active = True
        print(f"Activated {self.name}")

    def deactivate(self):
        """停用插件"""
        self.is_active = False
        print(f"Deactivated {self.name}")

    def unload(self):
        """卸载插件"""
        print(f"Unloading {self.name}")

    def pre_analysis(self, code: str) -> str:
        """代码分析前的处理"""
        # 自定义处理逻辑
        return code
```

#### 3. Hook 系统

**可用的 Action Hooks**:

- `workflow_start`: 工作流开始
- `workflow_stage_start`: 阶段开始
- `workflow_stage_end`: 阶段结束
- `workflow_complete`: 工作流完成
- `agent_execute_start`: 智能体执行开始
- `agent_execute_end`: 智能体执行结束

**可用的 Filter Hooks**:

- `before_code_analysis`: 代码分析前
- `after_code_generation`: 代码生成后
- `before_llm_call`: LLM调用前
- `after_llm_call`: LLM调用后

示例：

```python
# 注册 action hook
hook_manager.register_action(
    'workflow_start',
    self.on_workflow_start,
    priority=10
)

# 注册 filter hook
hook_manager.register_filter(
    'after_code_generation',
    self.modify_code,
    priority=10
)
```

#### 4. 测试插件

```bash
# 将插件目录放到 plugins/ 下
cp -r my-plugin /path/to/resoftai-cli/plugins/

# 重启服务
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload
```

#### 5. 发布到市场

1. 打包插件: `tar -czf my-plugin-1.0.0.tar.gz my-plugin/`
2. 上传到插件仓库
3. 提交市场审核

---

## 企业版功能

### 组织管理

#### 创建组织

访问 **组织管理** 页面，点击"创建组织"：

```
组织名称: 我的公司
Slug: my-company (唯一标识)
订阅级别:
  - 免费版: 5个项目, 10K API调用, 1GB存储, 3个成员
  - 入门版: 20个项目, 100K API调用, 10GB存储, 10个成员
  - 专业版: 100个项目, 1M API调用, 100GB存储, 50个成员
  - 企业版: 无限制
联系邮箱: admin@company.com
描述: 组织描述
```

#### 组织配置

- **订阅管理**: 升级/降级套餐
- **SSO配置**: 单点登录 (SAML, OAuth2, OIDC)
- **成员管理**: 邀请成员、设置权限
- **配额监控**: 实时查看资源使用情况
- **审计日志**: 完整的操作记录

### 团队管理

#### 创建团队

1. 选择组织
2. 点击"创建团队"
3. 填写团队信息：

```
团队名称: 开发团队
描述: 负责核心功能开发
默认团队: ✓ (新成员自动加入)
```

#### 团队角色

- **所有者 (OWNER)**: 完全控制权限
- **管理员 (ADMIN)**: 管理团队成员和设置
- **成员 (MEMBER)**: 正常使用权限
- **查看者 (VIEWER)**: 只读权限

#### 成员管理

1. 点击"成员管理"
2. 添加成员: 输入用户ID和角色
3. 修改角色: 变更成员权限
4. 移除成员: 从团队中移除

### RBAC 权限控制

#### 权限系统

基于角色的访问控制 (RBAC):

```python
# 权限示例
permissions = [
    "project.create",
    "project.read",
    "project.update",
    "project.delete",
    "team.manage",
    "organization.manage",
    "plugin.install",
    "quota.view"
]
```

#### 自定义角色

企业版支持创建自定义角色：

```json
{
  "name": "DevOps工程师",
  "permissions": [
    "project.read",
    "project.deploy",
    "plugin.manage",
    "quota.view"
  ]
}
```

### 配额管理

#### 查看配额

访问 **配额监控** 页面：

- **项目配额**: 可创建的项目数量
- **API调用配额**: 每月API调用次数
- **存储配额**: 文件存储空间
- **团队成员配额**: 可添加的成员数量
- **LLM Token配额**: 每月可用的Token数量

#### 配额告警

系统自动监控配额使用：

- **80%**: ⚠️ 警告提示
- **90%**: ⚠️ 严重警告
- **100%**: 🔴 配额耗尽，功能受限

#### 配额重置

- 按月重置: API调用、LLM Tokens
- 按需重置: 存储、项目数（需要手动清理）

### 审计日志

#### 查看日志

所有重要操作都会记录审计日志：

- 用户登录/登出
- 组织创建/修改/删除
- 团队操作
- 权限变更
- 项目操作
- 数据导出

#### 日志格式

```json
{
  "id": 123,
  "action": "CREATE",
  "resource_type": "organization",
  "resource_id": 1,
  "user_id": 10,
  "organization_id": 1,
  "description": "创建组织: 我的公司",
  "changes": {
    "tier": {"old": null, "new": "professional"}
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2025-11-14T10:30:00Z"
}
```

### SSO 单点登录

#### 支持的协议

- SAML 2.0
- OAuth 2.0
- OpenID Connect (OIDC)

#### 配置 SAML

1. 在组织设置中启用 SSO
2. 选择 SAML 提供商
3. 配置 IdP 元数据：

```json
{
  "entity_id": "https://idp.example.com",
  "sso_url": "https://idp.example.com/sso",
  "certificate": "-----BEGIN CERTIFICATE-----\n...",
  "attribute_mapping": {
    "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
    "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
  }
}
```

4. 测试SSO连接
5. 启用 SSO 强制登录

---

## 性能监控

### 性能仪表板

访问 **性能监控** 页面，查看实时性能指标。

#### 总览卡片

- **活跃工作流**: 当前正在执行的工作流数量
- **成功率**: 近24小时工作流成功率
- **平均完成时间**: 工作流平均耗时
- **Token使用量**: 今日LLM Token消耗
- **缓存命中率**: 智能体缓存命中率
- **活跃告警**: 当前性能告警数量

#### 告警列表

实时显示性能告警：

- 🔴 **错误**: 严重性能问题
- ⚠️ **警告**: 需要关注的问题
- ℹ️ **信息**: 一般性通知

### 工作流监控

**工作流统计** 标签页：

- 总执行次数
- 成功/失败次数
- 平均Token使用
- 各阶段耗时分布
- 缓存命中率趋势

**时间线图表**:
- X轴: 时间
- Y轴: 工作流执行次数
- 支持筛选: 7天、30天、90天

### 智能体监控

**智能体性能** 标签页：

查看每个智能体的详细性能：

- **项目经理**: 平均耗时 45秒, Token 1.2K
- **需求分析师**: 平均耗时 120秒, Token 3.5K
- **架构师**: 平均耗时 180秒, Token 5.2K
- **UI设计师**: 平均耗时 150秒, Token 4.8K
- **开发工程师**: 平均耗时 600秒, Token 15K
- **测试工程师**: 平均耗时 240秒, Token 6K
- **质量专家**: 平均耗时 180秒, Token 5K

**性能对比图表**:
- 柱状图: 各智能体耗时对比
- 饼图: Token使用分布

### 系统监控

**系统资源** 标签页：

- **CPU使用率**: 实时CPU占用
- **内存使用**: 当前内存占用
- **磁盘空间**: 存储空间使用情况
- **网络流量**: 上传/下载速度
- **数据库连接**: 活跃连接数

**健康检查**:
- 服务状态: ✅ 正常 / 🔴 异常
- 数据库连接: ✅ 正常
- LLM API: ✅ 可用
- WebSocket: ✅ 在线

### LLM 使用监控

**LLM统计** 标签页：

按提供商统计Token使用：

- **DeepSeek**: 125K tokens, ¥12.50
- **Anthropic**: 50K tokens, $5.00
- **Google Gemini**: 30K tokens, $1.50

**成本分析**:
- 总成本: ¥100.00
- 按项目分组
- 按智能体分组
- 成本趋势图

### 性能优化建议

系统自动提供优化建议：

1. **启用缓存**: 可减少30%的Token消耗
2. **并行执行**: 可提升40%的执行速度
3. **升级套餐**: 当前配额使用85%，建议升级
4. **清理旧项目**: 释放存储空间

### 导出报告

- **导出格式**: PDF, Excel, JSON
- **时间范围**: 自定义日期范围
- **包含内容**:
  - 性能汇总
  - 详细统计
  - 图表截图
  - 优化建议

---

## API 参考

### 认证

#### 注册用户

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

# 响应
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2025-11-14T10:00:00Z"
}
```

#### 登录

```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=SecurePass123!

# 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 刷新Token

```bash
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

# 响应
{
  "access_token": "new_access_token...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 项目管理

#### 创建项目

```bash
POST /api/projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "我的项目",
  "description": "项目描述",
  "requirements": "详细需求",
  "config": {
    "execution_strategy": "adaptive",
    "enable_cache": true
  }
}

# 响应
{
  "id": 1,
  "name": "我的项目",
  "status": "pending",
  "created_at": "2025-11-14T10:00:00Z"
}
```

#### 获取项目列表

```bash
GET /api/projects?skip=0&limit=20
Authorization: Bearer <access_token>

# 响应
[
  {
    "id": 1,
    "name": "项目1",
    "status": "completed",
    "progress": 100
  }
]
```

#### 启动工作流

```bash
POST /api/projects/{project_id}/execute
Authorization: Bearer <access_token>

# 响应
{
  "project_id": 1,
  "workflow_id": "wf_123456",
  "status": "running",
  "current_stage": "requirements_analysis"
}
```

### 文件管理

#### 上传文件

```bash
POST /api/files
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file=@/path/to/file.py
project_id=1

# 响应
{
  "id": 1,
  "filename": "file.py",
  "size": 1024,
  "version": 1
}
```

#### 下载文件

```bash
GET /api/files/{file_id}/download
Authorization: Bearer <access_token>
```

### 插件管理

#### 获取插件列表

```bash
GET /api/marketplace/plugins?category=development
Authorization: Bearer <access_token>

# 响应
[
  {
    "slug": "code-formatter",
    "name": "Code Formatter",
    "version": "1.0.0",
    "rating": 4.5,
    "downloads": 1000
  }
]
```

#### 安装插件

```bash
POST /api/marketplace/plugins/{slug}/install
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "version": "1.0.0",
  "auto_dependencies": true
}

# 响应
{
  "slug": "code-formatter",
  "status": "installed",
  "version": "1.0.0"
}
```

### 性能监控

#### 获取仪表板数据

```bash
GET /api/monitoring/dashboard/overview
Authorization: Bearer <access_token>

# 响应
{
  "active_workflows": 3,
  "success_rate": 95.5,
  "avg_completion_time_seconds": 450,
  "total_tokens_used_today": 125000,
  "cache_hit_rate": 0.65,
  "active_alerts": 2
}
```

#### 获取工作流统计

```bash
GET /api/monitoring/workflows/stats?days=7
Authorization: Bearer <access_token>

# 响应
{
  "total": 50,
  "successful": 47,
  "failed": 3,
  "avg_tokens": 25000,
  "cache_hit_rate": 0.65
}
```

### WebSocket 实时更新

#### 连接 WebSocket

```javascript
import io from 'socket.io-client'

const socket = io('http://localhost:8000', {
  auth: {
    token: 'your_access_token'
  }
})

// 订阅项目更新
socket.emit('subscribe_project', { project_id: 1 })

// 接收更新
socket.on('project_update', (data) => {
  console.log('Project update:', data)
})

// 接收智能体活动
socket.on('agent_activity', (data) => {
  console.log('Agent activity:', data)
})
```

---

## 故障排查

### 常见问题

#### 1. 数据库连接失败

**症状**: 启动时报错 "Could not connect to database"

**解决方案**:

```bash
# 检查数据库是否运行
psql -h localhost -U postgres -c "SELECT version();"

# 检查 DATABASE_URL 配置
echo $DATABASE_URL

# SQLite 用户：确保文件路径正确
ls -l resoftai.db

# PostgreSQL 用户：检查连接字符串
# 格式: postgresql+asyncpg://user:password@host:port/dbname
```

#### 2. LLM API 调用失败

**症状**: 智能体执行时报错 "LLM API call failed"

**解决方案**:

```bash
# 检查 API Key 是否正确
echo $DEEPSEEK_API_KEY

# 测试 API 连接
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'

# 检查配额是否耗尽
# 登录 DeepSeek 控制台查看余额
```

#### 3. 前端无法连接后端

**症状**: 前端页面显示 "Network Error"

**解决方案**:

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 检查 CORS 配置
# 确保 .env 中 CORS_ORIGINS 包含前端地址
CORS_ORIGINS=http://localhost:3000

# 检查防火墙
sudo ufw status
sudo ufw allow 8000
```

#### 4. 工作流执行卡住

**症状**: 工作流长时间停留在某个阶段

**解决方案**:

```bash
# 查看日志
tail -f logs/resoftai.log

# 检查是否有错误信息
grep ERROR logs/resoftai.log

# 重启工作流
# 通过前端"终止"然后"重新启动"

# 如果有检查点，可以从断点恢复
```

#### 5. 内存不足

**症状**: 系统缓慢或崩溃

**解决方案**:

```bash
# 检查内存使用
free -h

# 检查进程内存占用
ps aux | grep python | sort -k4 -r

# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 优化配置：减少并发工作流数量
# 在 .env 中设置
MAX_CONCURRENT_WORKFLOWS=2
```

### 日志分析

#### 日志位置

- 应用日志: `logs/resoftai.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

#### 日志级别

```python
# .env 配置
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### 常见错误代码

- **E001**: 数据库连接失败
- **E002**: LLM API 调用失败
- **E003**: 文件操作失败
- **E004**: 工作流执行失败
- **E005**: 权限不足

### 性能调优

#### 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_files_project_id ON files(project_id);

-- 分析查询性能
EXPLAIN ANALYZE SELECT * FROM projects WHERE user_id = 1;

-- 清理旧数据
DELETE FROM agent_activities WHERE created_at < NOW() - INTERVAL '90 days';
```

#### 缓存配置

```python
# 在项目配置中启用缓存
{
  "cache_config": {
    "enabled": true,
    "ttl": 3600,  # 1小时
    "max_size": 1000  # 最多缓存1000个结果
  }
}
```

#### 并行执行

```python
# 启用并行执行
{
  "execution_strategy": "parallel",
  "parallel_stages": ["architecture", "ui_design"]
}
```

### 备份与恢复

#### 备份数据库

```bash
# PostgreSQL
pg_dump resoftai > backup_$(date +%Y%m%d).sql

# SQLite
cp resoftai.db backup_$(date +%Y%m%d).db
```

#### 恢复数据库

```bash
# PostgreSQL
psql resoftai < backup_20251114.sql

# SQLite
cp backup_20251114.db resoftai.db
```

#### 备份文件

```bash
# 备份 workspace 目录
tar -czf workspace_backup_$(date +%Y%m%d).tar.gz workspace/

# 恢复
tar -xzf workspace_backup_20251114.tar.gz
```

---

## 常见问题

### 功能相关

**Q: 支持哪些编程语言？**

A: 开发智能体支持生成多种语言的代码：Python, JavaScript/TypeScript, Java, Go, Rust, C++, C#, PHP 等。代码质量检查支持以上9种语言。

**Q: 可以自定义智能体吗？**

A: 目前不支持自定义智能体，但可以通过插件系统扩展智能体功能。未来版本将支持自定义智能体。

**Q: 生成的代码质量如何？**

A: 开发智能体集成了代码质量检查，对生成的代码进行：
- 安全漏洞扫描
- 最佳实践验证
- 命名规范检查
- 复杂度分析
- 自动评分（0-100分）

通常生成的代码评分在70-90分之间。

**Q: 支持私有化部署吗？**

A: 是的，支持完全私有化部署。您可以部署在自己的服务器上，不需要连接外网（LLM API除外）。

### 计费相关

**Q: 如何计费？**

A: ResoftAI 本身是开源的，不收费。但使用 LLM API 需要自行承担费用：
- DeepSeek: ¥0.001/1K tokens
- Anthropic Claude: $0.01/1K tokens
- Google Gemini: $0.0005/1K tokens

**Q: 如何控制成本？**

A: 多种方式控制成本：
1. 启用缓存：减少30%的API调用
2. 使用更便宜的模型（如DeepSeek）
3. 设置配额限制
4. 优化 Prompt
5. 并行执行减少总耗时

**Q: 企业版如何计费？**

A: 企业版功能目前免费开放。未来可能推出订阅计划，但会提供充足的通知期。

### 技术相关

**Q: 最低硬件要求是什么？**

A:
- CPU: 2核
- 内存: 4GB
- 磁盘: 10GB
- 网络: 稳定的互联网连接（用于LLM API）

**Q: 支持 Windows 吗？**

A: 支持，但推荐使用 WSL (Windows Subsystem for Linux) 以获得更好的兼容性。

**Q: 可以离线使用吗？**

A: 部分功能可以离线使用（项目管理、文件管理等），但智能体执行需要连接 LLM API，因此必须在线。未来可能支持本地LLM。

**Q: 支持集群部署吗？**

A: 当前版本主要面向单机部署。集群部署功能在开发计划中。

### 安全相关

**Q: 数据安全如何保障？**

A:
- 数据库密码使用 Argon2 哈希
- JWT Token 过期机制
- HTTPS 加密传输（生产环境）
- 输入验证和 SQL 注入防护
- 审计日志记录所有敏感操作

**Q: LLM API 调用时数据会泄露吗？**

A: 数据会发送到 LLM 提供商进行处理。建议：
- 不要在需求中包含敏感信息
- 使用支持私有部署的 LLM（如Azure OpenAI）
- 定期审查审计日志

**Q: 支持 SSO 单点登录吗？**

A: 企业版支持 SAML、OAuth2 和 OIDC 协议的 SSO。

---

## 最佳实践

### 需求编写

**1. 明确具体**

❌ 差的需求:
```
做一个网站
```

✅ 好的需求:
```
开发一个在线图书管理系统，包括以下功能：
1. 用户注册、登录（JWT认证）
2. 图书信息管理（增删改查）
3. 图书借阅管理
4. 借阅历史记录
5. 到期提醒

技术栈：
- 后端: FastAPI + PostgreSQL
- 前端: React + Ant Design
- 部署: Docker
```

**2. 分阶段实施**

对于大型项目，分成多个小项目：

```
第一阶段：用户认证系统
第二阶段：核心业务功能
第三阶段：辅助功能和优化
```

**3. 提供示例**

```
用户界面样式参考: https://example.com/design
类似项目: GitHub的项目管理功能
```

### 工作流配置

**1. 选择合适的执行策略**

- **Sequential**: 串行执行，适合需要严格顺序的项目
- **Parallel**: 并行执行，适合独立模块较多的项目
- **Adaptive**: 自适应，系统自动选择最优策略（推荐）

**2. 启用缓存**

```python
{
  "enable_cache": true,  # 推荐开启
  "cache_ttl": 3600      # 缓存1小时
}
```

缓存可以减少30%的LLM调用，特别适合：
- 迭代开发
- 类似项目
- 调试阶段

**3. 启用检查点**

```python
{
  "enable_checkpoints": true,  # 推荐开启
  "checkpoint_interval": 300   # 每5分钟保存
}
```

好处：
- 意外中断可恢复
- 长时间执行的项目更安全
- 方便调试

### 代码质量

**1. 遵循语言规范**

在需求中明确代码风格：

```
代码风格：
- Python: PEP 8
- JavaScript: ESLint (Airbnb)
- 命名: 驼峰式
- 注释: 完整的函数文档字符串
```

**2. 包含测试要求**

```
测试要求：
- 单元测试覆盖率 > 80%
- 使用 pytest
- 包含 fixtures 和 mock
```

**3. 安全检查**

开发智能体会自动检查：
- SQL 注入
- XSS 攻击
- 硬编码密钥
- 不安全的加密

但仍需人工审查敏感代码。

### 性能优化

**1. 并行执行**

```python
{
  "execution_strategy": "parallel",
  "parallel_stages": [
    "architecture_design",
    "ui_design"
  ]
}
```

架构设计和UI设计可以并行，节省40%时间。

**2. 减少Token消耗**

- 精简需求描述
- 使用模板而非从头生成
- 启用缓存
- 选择高效的 LLM（如 DeepSeek）

**3. 监控性能**

定期查看性能监控：
- 识别慢速智能体
- 优化 Prompt
- 调整超时设置

### 团队协作

**1. 组织结构**

```
组织: 我的公司
├── 开发团队
│   ├── 后端开发组
│   └── 前端开发组
├── 测试团队
└── DevOps团队
```

**2. 权限分配**

- **管理员**: 组织配置、计费
- **项目经理**: 项目管理、成员分配
- **开发者**: 创建和执行项目
- **查看者**: 只读访问

**3. 配额规划**

为不同团队分配配额：

```
开发团队: 50个项目, 500K tokens/月
测试团队: 20个项目, 200K tokens/月
```

### 成本控制

**1. 选择合适的 LLM**

| 提供商 | 价格 | 适用场景 |
|--------|------|---------|
| DeepSeek | ¥0.001/1K | 开发、测试（推荐）|
| Claude | $0.01/1K | 复杂架构设计 |
| Gemini | $0.0005/1K | 简单任务 |

**2. 使用模板**

预定义项目模板可以减少80%的生成成本。

**3. 定期清理**

- 删除旧项目
- 清理缓存文件
- 归档完成的项目

**4. 设置配额告警**

在达到80%时收到通知，避免超支。

### 安全实践

**1. 环境变量**

永远不要在代码中硬编码密钥：

```python
# ❌ 错误
API_KEY = "sk-xxxxx"

# ✅ 正确
import os
API_KEY = os.getenv("API_KEY")
```

**2. 定期更新**

```bash
# 每月更新依赖
pip install --upgrade -r requirements.txt

# 检查安全漏洞
pip-audit
```

**3. 备份**

设置自动备份：

```bash
# 添加到 crontab
0 2 * * * /path/to/backup.sh
```

**4. 审计日志**

定期审查审计日志，特别是：
- 权限变更
- 数据导出
- 配置修改

---

## 附录

### A. 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+K | 全局搜索 |
| Ctrl+S | 保存文件 |
| Ctrl+N | 新建项目 |
| Ctrl+E | 启动工作流 |
| Ctrl+, | 打开设置 |

### B. API 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

### C. 数据库Schema

主要表结构参考：

```sql
-- 用户表
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(200) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  is_admin BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 项目表
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  name VARCHAR(200) NOT NULL,
  description TEXT,
  status VARCHAR(50),
  progress INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
```

完整 Schema 请参考: `alembic/versions/`

### D. 环境变量完整清单

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/resoftai

# JWT认证
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM提供商
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
ANTHROPIC_API_KEY=sk-ant-xxxxx
GOOGLE_API_KEY=AIzaSyxxxxx

# 应用配置
WORKSPACE_DIR=./workspace
MAX_UPLOAD_SIZE=104857600  # 100MB
LOG_LEVEL=INFO
LOG_FILE=logs/resoftai.log

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=true

# 性能
MAX_CONCURRENT_WORKFLOWS=5
WORKFLOW_TIMEOUT=3600  # 1小时
CACHE_TTL=3600

# 企业功能
ENABLE_SSO=false
ENABLE_AUDIT_LOG=true
```

### E. 支持与社区

- **文档**: https://docs.resoftai.com
- **GitHub**: https://github.com/yourusername/resoftai-cli
- **问题反馈**: https://github.com/yourusername/resoftai-cli/issues
- **讨论区**: https://github.com/yourusername/resoftai-cli/discussions
- **邮件支持**: support@resoftai.com

### F. 更新日志

**v0.2.2 (2025-11-14)**
- ✨ 新增插件市场前端
- ✨ 新增企业管理前端
- ⚡ 工作流性能优化40-60%
- 📊 全面的性能监控系统
- 🔧 优化的工作流引擎
- 🐛 修复若干已知问题

**v0.2.1 (2025-11-10)**
- ✨ 新增企业版功能
- ✨ 新增插件系统
- ✨ 新增协作编辑
- 📊 性能监控后端
- 🔧 LLM抽象层优化

**v0.2.0 (2025-11-01)**
- 🎉 首个公开测试版本
- 🤖 7个专业智能体
- 🔄 完整工作流引擎
- 📁 项目和文件管理
- 🎨 Vue 3 前端界面

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

---

## 致谢

感谢所有为 ResoftAI 项目做出贡献的开发者和用户！

**ResoftAI 团队**
2025年11月
