# ResoftAI 开发者指南

本指南帮助开发者快速搭建 ResoftAI 本地开发环境。

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [开发工具](#开发工具)
- [调试指南](#调试指南)
- [测试指南](#测试指南)
- [代码规范](#代码规范)
- [常见问题](#常见问题)

## 🔧 环境要求

### 必需

- **Python**: 3.11+
- **PostgreSQL**: 15+ (或 Docker)
- **Git**: 2.x+

### 推荐

- **Docker & Docker Compose**: 用于容器化开发
- **VSCode**: 推荐的 IDE（已包含配置文件）
- **Make**: 用于简化命令（Linux/Mac 自带，Windows 需安装）

## 🚀 快速开始

### 方式一：本地开发（推荐用于调试）

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/resoftai-cli.git
cd resoftai-cli

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. 安装依赖
make install
# 或手动: pip install -r requirements.txt

# 4. 配置环境变量
make setup
# 或手动: cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 5. 启动数据库（使用 Docker）
docker-compose up -d postgres

# 6. 运行数据库迁移
make db-upgrade
# 或: alembic upgrade head

# 7. 启动开发服务器
make dev
# 或: PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload
```

访问 http://localhost:8000/docs 查看 API 文档

### 方式二：Docker 开发（更简单）

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/resoftai-cli.git
cd resoftai-cli

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动完整开发环境
make docker-dev

# 查看日志
make docker-logs

# 停止环境
make docker-down
```

开发环境服务：
- **API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **Adminer (数据库 UI)**: http://localhost:8080
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 🛠️ 开发工具

### Makefile 命令

```bash
# 查看所有可用命令
make help

# 开发相关
make dev              # 启动开发服务器（热重载）
make shell            # 启动 IPython shell
make dev-cli          # 启动 CLI

# 测试相关
make test             # 运行所有测试
make test-cov         # 运行测试并生成覆盖率报告
make test-watch       # 监视模式运行测试

# 代码质量
make lint             # 运行所有 linters
make format           # 格式化代码
make format-check     # 检查代码格式

# 数据库
make db-upgrade       # 运行数据库迁移
make db-downgrade     # 回滚最后一次迁移
make db-reset         # 重置数据库
make db-revision      # 创建新迁移
make db-shell         # 连接到数据库

# Docker
make docker-dev       # 启动 Docker 开发环境
make docker-logs      # 查看日志
make docker-down      # 停止环境
make docker-rebuild   # 重建镜像
make docker-clean     # 清理资源

# 清理
make clean            # 清理生成的文件
make clean-all        # 深度清理
```

### VSCode 调试

项目包含完整的 VSCode 配置：

1. **Python: FastAPI** - 调试 API 服务器
2. **Python: CLI** - 调试 CLI 工具
3. **Python: Current Test File** - 调试当前测试文件
4. **Python: All Tests** - 调试所有测试
5. **Docker: Attach to Backend** - 连接到 Docker 容器进行调试

使用方法：
1. 打开 VSCode
2. 按 F5 或点击调试面板
3. 选择对应的调试配置
4. 设置断点并开始调试

### VSCode 任务

项目包含预配置的任务（Ctrl+Shift+B）：

- **Run Tests** - 运行测试
- **Run Tests with Coverage** - 带覆盖率的测试
- **Format Code** - 格式化代码
- **Lint Code** - 检查代码
- **Run Dev Server** - 启动开发服务器
- **Database Upgrade** - 数据库迁移

## 🐛 调试指南

### 使用 debugpy 远程调试（Docker）

1. 启动开发环境：
```bash
make docker-dev
```

2. 在 VSCode 中选择 "Docker: Attach to Backend" 配置

3. 在代码中设置断点

4. 发送请求触发断点

### 使用 ipdb 调试

在代码中插入：
```python
import ipdb; ipdb.set_trace()
```

或在测试中：
```python
pytest tests/test_something.py -s  # -s 允许 pdb 交互
```

### 日志调试

开发环境日志配置在 `logging.dev.yml`：

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("详细调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
```

日志文件位置：
- `logs/resoftai-dev.log` - 所有日志
- `logs/resoftai-errors.log` - 仅错误日志
- `logs/resoftai-json.log` - JSON 格式日志

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
make test

# 运行特定文件
PYTHONPATH=src pytest tests/test_agents.py -v

# 运行特定测试
PYTHONPATH=src pytest tests/test_agents.py::test_agent_creation -v

# 带覆盖率
make test-cov

# 监视模式（文件改动自动重新运行）
make test-watch

# 并行运行（更快）
PYTHONPATH=src pytest tests/ -n auto
```

### 编写测试

测试文件结构：
```
tests/
├── test_core/          # 核心功能测试
├── test_agents/        # 智能体测试
├── test_api/           # API 测试
├── test_integration/   # 集成测试
└── conftest.py         # 测试配置
```

示例测试：
```python
import pytest
from resoftai.agents.developer import DeveloperAgent

@pytest.mark.asyncio
async def test_developer_agent(message_bus, project_state, llm_config):
    """Test developer agent functionality."""
    agent = DeveloperAgent(
        role=AgentRole.DEVELOPER,
        message_bus=message_bus,
        project_state=project_state,
        llm_config=llm_config
    )

    assert agent.name == "Developer"
    assert len(agent.capabilities) > 0
```

### 测试覆盖率

```bash
# 生成 HTML 覆盖率报告
make test-cov

# 打开报告
open htmlcov/index.html
```

目标覆盖率：
- 总体: 80%+
- 核心模块: 90%+
- API 路由: 95%+

## 📐 代码规范

### Python 代码风格

遵循 PEP 8，使用 Black 格式化：

```bash
# 自动格式化
make format

# 检查格式
make format-check

# 运行 linters
make lint
```

### 代码组织

```
src/resoftai/
├── core/           # 核心组件（agent, workflow, state）
├── agents/         # AI 智能体实现
├── api/            # FastAPI 路由
├── models/         # SQLAlchemy 模型
├── llm/            # LLM 提供者
├── orchestration/  # 工作流编排
└── templates/      # 项目模板
```

### 命名约定

- **文件名**: snake_case (如 `developer_agent.py`)
- **类名**: PascalCase (如 `DeveloperAgent`)
- **函数/变量**: snake_case (如 `create_agent`)
- **常量**: UPPER_CASE (如 `MAX_RETRIES`)
- **私有方法**: _leading_underscore (如 `_internal_method`)

### 导入顺序

```python
# 1. 标准库
import os
import sys

# 2. 第三方库
import pytest
from fastapi import FastAPI

# 3. 本地导入
from resoftai.core.agent import Agent
from resoftai.models.user import User
```

### 类型提示

使用类型提示提高代码可读性：

```python
from typing import List, Optional

def create_agents(count: int) -> List[Agent]:
    """Create multiple agents."""
    agents: List[Agent] = []
    # ...
    return agents

async def get_user(user_id: int) -> Optional[User]:
    """Get user by ID."""
    # ...
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def complex_function(param1: str, param2: int) -> bool:
    """
    执行复杂操作的简短描述。

    更详细的说明可以写在这里。支持多行。

    Args:
        param1: 第一个参数的描述
        param2: 第二个参数的描述

    Returns:
        操作是否成功

    Raises:
        ValueError: 当参数无效时
        RuntimeError: 当操作失败时

    Example:
        >>> complex_function("test", 42)
        True
    """
    # 实现...
```

## ❓ 常见问题

### Q: 数据库连接错误

**A**: 确保 PostgreSQL 正在运行：

```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 启动 PostgreSQL
docker-compose up -d postgres

# 检查连接
psql postgresql://postgres:postgres@localhost:5432/resoftai
```

### Q: 导入错误 "No module named 'resoftai'"

**A**: 设置 PYTHONPATH：

```bash
export PYTHONPATH=src  # Linux/Mac
set PYTHONPATH=src     # Windows CMD
$env:PYTHONPATH="src"  # Windows PowerShell
```

或使用 `make` 命令（自动设置）。

### Q: 端口被占用

**A**: 更改端口或停止占用进程：

```bash
# 查找占用端口的进程
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# 停止进程
kill -9 <PID>  # Linux/Mac
taskkill /F /PID <PID>  # Windows

# 或在 .env 中更改端口
API_PORT=8001
```

### Q: 测试失败

**A**: 常见原因和解决方法：

```bash
# 1. 清理缓存
make clean

# 2. 确保测试数据库存在
createdb resoftai_test

# 3. 重新运行迁移
make db-reset

# 4. 查看详细错误
PYTHONPATH=src pytest tests/ -v -s --tb=long
```

### Q: Docker 容器无法启动

**A**:

```bash
# 查看日志
docker-compose -f docker-compose.dev.yml logs backend

# 重建镜像
make docker-rebuild

# 清理并重新开始
make docker-clean
make docker-dev
```

## 📚 其他资源

- [API 文档](http://localhost:8000/docs)
- [项目路线图](ROADMAP.md)
- [贡献指南](CONTRIBUTING.md)
- [测试文档](TESTING.md)

## 🤝 获取帮助

遇到问题？

1. 查看本文档和 FAQ
2. 查看 [Issues](https://github.com/your-org/resoftai-cli/issues)
3. 在 Discord/Slack 社区提问
4. 提交新 Issue

---

**Happy Coding! 🎉**
