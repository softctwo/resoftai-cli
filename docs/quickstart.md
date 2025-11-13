# ResoftAI 快速启动指南

## 5分钟快速上手

本指南帮助您在5分钟内快速体验ResoftAI多智能体平台。

### 前置要求

- Python 3.9 或更高版本
- Anthropic Claude API密钥

### 步骤1: 安装

```bash
# 克隆仓库
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 安装依赖
pip install -r requirements.txt

# 或使用开发模式安装
pip install -e .
```

### 步骤2: 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置您的API密钥
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 步骤3: 验证安装

```bash
# 检查CLI是否正常工作
resoftai --version

# 查看平台信息
resoftai info

# 查看帮助
resoftai --help
```

### 步骤4: 创建第一个项目

```bash
# 使用CLI创建项目
resoftai create "开发一个博客系统，支持文章发布、评论和用户管理" --name "博客系统"

# 或指定输出目录
resoftai create "任务管理系统" --name "任务管理" --output ./my-project
```

### 步骤5: 查看结果

项目完成后，您将获得：

```
workspace/项目名称/
├── documentation/           # 完整的项目文档
│   ├── requirements-specification.md
│   ├── design-specification.md
│   ├── database-design.md
│   ├── deployment-guide.md
│   ├── user-manual.md
│   └── training-manual.md
└── project_state.json      # 项目状态文件
```

### 步骤6: 查看项目状态

```bash
# 查看项目状态
resoftai status workspace/博客系统/project_state.json
```

## 使用Python API

```python
import asyncio
from resoftai.core.message_bus import MessageBus
from resoftai.core.state import ProjectState
from resoftai.core.workflow import ProjectWorkflow
from resoftai.agents import ProjectManagerAgent, RequirementsAnalystAgent

async def main():
    # 初始化
    message_bus = MessageBus()
    project_state = ProjectState(
        name="我的项目",
        description="项目需求"
    )
    workflow = ProjectWorkflow(message_bus, project_state)

    # 创建智能体
    agents = [
        ProjectManagerAgent(
            role=AgentRole.PROJECT_MANAGER,
            message_bus=message_bus,
            project_state=project_state
        ),
        # ... 其他智能体
    ]

    # 启动工作流
    await workflow.start("项目需求")

asyncio.run(main())
```

## 使用Web API

### 启动API服务器

```bash
python -m resoftai.api.server
```

服务器将在 `http://localhost:8000` 启动。

### 创建项目（API）

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "电商平台",
    "requirements": "开发一个完整的电商平台..."
  }'
```

### 查看项目状态

```bash
curl "http://localhost:8000/projects/{project_id}/status"
```

### API文档

访问 `http://localhost:8000/docs` 查看完整的API文档（Swagger UI）。

## 运行示例

### 基础示例

```bash
python examples/example_usage.py
```

### 自定义智能体示例

```bash
python examples/custom_agent_example.py
```

## 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_core.py

# 生成覆盖率报告
pytest --cov=resoftai --cov-report=html
```

## 自定义扩展

### 创建自定义智能体

```python
from resoftai.core.agent import Agent, AgentRole, AgentCapability
from resoftai.core.state import WorkflowStage

class MyCustomAgent(Agent):
    @property
    def name(self) -> str:
        return "My Custom Agent"

    @property
    def system_prompt(self) -> str:
        return "You are a custom agent with specific expertise..."

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="custom_task",
                description="Perform custom task",
                input_schema={},
                output_schema={}
            )
        ]

    @property
    def responsible_stages(self) -> List[WorkflowStage]:
        return [WorkflowStage.IMPLEMENTATION]

    async def process_request(self, message: Message) -> None:
        # 实现请求处理逻辑
        pass

    async def handle_task_assignment(self, message: Message) -> None:
        # 实现任务处理逻辑
        pass
```

详细示例请参考 `examples/custom_agent_example.py`。

### 添加新的文档生成器

```python
from resoftai.generators.base import DocumentGenerator

class MyDocumentGenerator(DocumentGenerator):
    @property
    def document_name(self) -> str:
        return "My Custom Document"

    @property
    def document_filename(self) -> str:
        return "my-custom-doc.md"

    async def generate_content(self) -> str:
        # 生成文档内容
        return "# My Document\n\nContent here..."
```

## 常见问题

### API密钥错误

确保在 `.env` 文件中设置了有效的 `ANTHROPIC_API_KEY`：

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 导入错误

确保已安装所有依赖：

```bash
pip install -r requirements.txt
pip install pydantic-settings  # 如果缺失
```

### 权限错误

确保工作空间目录有写入权限：

```bash
mkdir -p /tmp/resoftai-workspace
chmod 755 /tmp/resoftai-workspace
```

## 下一步

- 📖 阅读完整的 [README](../README.md)
- 🏗️ 查看 [系统架构文档](architecture.md)
- 🔧 探索 [examples/](../examples/) 目录中的更多示例
- 💡 参与贡献或提交issue

## 获取帮助

- GitHub Issues: https://github.com/softctwo/resoftai-cli/issues
- 文档: https://github.com/softctwo/resoftai-cli/docs
- 邮箱: softctwo@aliyun.com

---

**享受使用ResoftAI多智能体平台！** 🚀
