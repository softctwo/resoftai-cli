# ResoftAI - 多智能体软件开发协作平台

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> AI驱动的软件定制开发服务平台，通过多智能体协作自动化完成从需求到交付的全流程

## 📋 项目简介

ResoftAI 是一个创新的多智能体协作平台，专为软件定制开发服务而设计。平台集成了7个专业AI智能体，模拟真实软件开发团队的协作模式，能够自动化完成从需求收集到最终交付的整个软件开发生命周期。

### 核心特性

- **🤖 7个专业AI智能体**
  - 项目经理 (Project Manager)
  - 需求分析师 (Requirements Analyst)
  - 软件架构师 (Software Architect)
  - UX/UI设计师 (UX/UI Designer)
  - 开发工程师 (Developer)
  - 测试工程师 (Test Engineer)
  - 质量专家 (Quality Expert)

- **📊 完整的工作流引擎**
  - 需求收集与分析
  - 架构设计
  - UI/UX设计
  - 原型开发
  - 客户评审
  - 开发计划
  - 实施与测试
  - 质量保证
  - 文档生成
  - 部署交付

- **📚 全套文档自动生成**
  - 需求规格说明书 (SRS)
  - 系统设计文档
  - 数据库设计文档
  - 部署安装指南
  - 用户使用手册
  - 培训手册

- **🎯 多种交互方式**
  - CLI 命令行工具
  - RESTful Web API
  - 实时进度追踪

## 🏗️ 系统架构

```
resoftai-cli/
├── src/resoftai/
│   ├── core/                # 核心组件
│   │   ├── agent.py         # 智能体基类
│   │   ├── workflow.py      # 工作流引擎
│   │   ├── message_bus.py   # 消息总线
│   │   └── state.py         # 状态管理
│   ├── agents/              # 专业智能体
│   │   ├── project_manager.py
│   │   ├── requirements_analyst.py
│   │   ├── architect.py
│   │   ├── uxui_designer.py
│   │   ├── developer.py
│   │   ├── test_engineer.py
│   │   └── quality_expert.py
│   ├── workflows/           # 工作流定义
│   ├── generators/          # 文档生成器
│   ├── cli/                 # CLI界面
│   ├── api/                 # Web API
│   └── config/              # 配置管理
├── tests/                   # 测试用例
├── examples/                # 使用示例
└── docs/                    # 文档
```

## 🚀 快速开始

### 环境要求

- Python 3.9 或更高版本
- Anthropic Claude API密钥

### 安装

1. 克隆仓库

```bash
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

或使用开发模式安装：

```bash
pip install -e .
```

3. 配置环境变量

复制 `.env.example` 到 `.env` 并配置您的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
RESOFTAI_WORKSPACE=/path/to/workspace
```

### 使用CLI创建项目

```bash
# 基本用法
resoftai create "开发一个任务管理系统，支持用户登录、任务创建、分配和追踪" --name "任务管理系统"

# 指定输出目录
resoftai create "电商平台需求..." --name "电商平台" --output ./my-project

# 查看项目状态
resoftai status ./workspace/my-project/project_state.json

# 查看平台信息
resoftai info
```

### 使用Web API

启动API服务器：

```bash
python -m resoftai.api.server
```

API将在 `http://localhost:8000` 运行。

创建项目（API调用示例）：

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "电商平台",
    "requirements": "开发一个完整的电商平台..."
  }'
```

查看项目状态：

```bash
curl "http://localhost:8000/projects/{project_id}/status"
```

### Python代码示例

```python
import asyncio
from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState
from resoftai.core.workflow import ProjectWorkflow
from resoftai.agents import ProjectManagerAgent, RequirementsAnalystAgent

async def main():
    # 初始化组件
    message_bus = MessageBus()
    project_state = ProjectState(
        name="我的项目",
        description="项目需求描述"
    )
    workflow = ProjectWorkflow(message_bus, project_state)

    # 初始化智能体
    agents = [
        ProjectManagerAgent(message_bus, project_state),
        RequirementsAnalystAgent(message_bus, project_state),
        # ... 其他智能体
    ]

    # 启动工作流
    await workflow.start("项目需求描述")

    # 处理工作流阶段
    for stage in workflow.WORKFLOW_SEQUENCE:
        await workflow.advance_to_stage(stage)
        # ... 处理逻辑

asyncio.run(main())
```

## 📖 工作流程详解

### 1. 需求收集与分析
- 项目经理收集初始需求
- 需求分析师详细分析和文档化需求
- 生成需求规格说明书

### 2. 架构与设计
- 架构师设计系统架构和数据库
- UX/UI设计师设计用户界面和体验
- 生成设计文档

### 3. 原型与评审
- 开发工程师创建原型
- 项目经理组织客户评审
- 收集反馈并优化需求

### 4. 开发计划
- 项目经理制定开发计划
- 任务分解和资源分配
- 时间表和里程碑

### 5. 实施与测试
- 开发工程师实现功能
- 测试工程师设计和执行测试
- 质量专家进行质量保证

### 6. 文档与交付
- 自动生成所有项目文档
- 创建部署指南和用户手册
- 完成最终交付

## 🎯 生成的交付物

每个项目完成后，平台将自动生成以下文档：

1. **需求规格说明书** - 详细的功能和非功能需求
2. **系统设计文档** - 架构设计和技术方案
3. **数据库设计文档** - 完整的数据模型和表结构
4. **部署安装指南** - 系统部署和配置说明
5. **用户使用手册** - 面向最终用户的操作指南
6. **培训手册** - 完整的培训课程和练习

## 🔧 配置选项

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| ANTHROPIC_API_KEY | Claude API密钥 | (必需) |
| CLAUDE_MODEL | 使用的Claude模型 | claude-3-5-sonnet-20241022 |
| CLAUDE_MAX_TOKENS | 最大生成令牌数 | 8192 |
| CLAUDE_TEMPERATURE | 温度参数 | 0.7 |
| RESOFTAI_WORKSPACE | 工作空间目录 | /tmp/resoftai-workspace |
| RESOFTAI_LOG_LEVEL | 日志级别 | INFO |
| API_HOST | API服务器地址 | 0.0.0.0 |
| API_PORT | API服务器端口 | 8000 |

## 🧪 测试

运行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_core.py

# 生成覆盖率报告
pytest --cov=resoftai --cov-report=html
```

## 📚 API文档

启动API服务器后，访问以下地址查看自动生成的API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要API端点

- `POST /projects` - 创建新项目
- `GET /projects/{project_id}` - 获取项目详情
- `GET /projects/{project_id}/status` - 获取项目状态
- `GET /projects/{project_id}/tasks` - 获取项目任务列表
- `GET /projects/{project_id}/artifacts` - 获取生成的文档

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- **softctwo** - [softctwo@aliyun.com](mailto:softctwo@aliyun.com)

## 🙏 致谢

- Anthropic Claude AI
- Python开源社区
- 所有贡献者

## 📞 联系方式

- 邮箱: softctwo@aliyun.com
- 项目主页: https://github.com/softctwo/resoftai-cli
- 问题反馈: https://github.com/softctwo/resoftai-cli/issues

## 🗺️ 路线图

- [ ] 支持更多AI模型（OpenAI GPT, etc.）
- [ ] Web前端界面
- [ ] 实时协作功能
- [ ] 项目模板库
- [ ] 代码生成功能
- [ ] 持续集成/部署支持
- [ ] 多语言支持
- [ ] 云服务部署

## 📊 项目状态

当前版本: **0.1.0** (Alpha)

- ✅ 核心框架完成
- ✅ 7个专业智能体实现
- ✅ 工作流引擎
- ✅ 文档生成系统
- ✅ CLI界面
- ✅ Web API
- ⏳ 生产环境优化
- ⏳ 性能优化
- ⏳ 更多测试覆盖

---

**注意**: 本项目目前处于Alpha阶段，建议在测试环境中使用。生产环境使用请谨慎。
