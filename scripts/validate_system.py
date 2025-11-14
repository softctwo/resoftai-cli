#!/usr/bin/env python3
"""
ResoftAI 系统验证脚本

此脚本执行全面的系统检查，验证所有组件是否正确配置并可以运行。
"""

import sys
import os
from pathlib import Path
import importlib.util

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(text):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def check_python_version():
    """检查Python版本"""
    print_header("检查Python版本")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print_success("Python版本符合要求 (3.11+)")
        return True
    else:
        print_error(f"Python版本不符合要求。需要3.11+，当前: {version.major}.{version.minor}")
        return False

def check_dependencies():
    """检查Python依赖"""
    print_header("检查Python依赖")

    required_packages = [
        ("fastapi", "FastAPI Web框架"),
        ("sqlalchemy", "SQLAlchemy ORM"),
        ("pydantic", "数据验证"),
        ("alembic", "数据库迁移"),
        ("anthropic", "Anthropic SDK"),
        ("httpx", "HTTP客户端"),
        ("socketio", "WebSocket支持"),
        ("pytest", "测试框架"),
    ]

    all_ok = True
    for package, description in required_packages:
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, "__version__", "未知")
            print_success(f"{description} ({package}): {version}")
        except ImportError:
            print_error(f"{description} ({package}): 未安装")
            all_ok = False

    return all_ok

def check_file_structure():
    """检查文件结构"""
    print_header("检查项目文件结构")

    root = Path(__file__).parent.parent

    required_paths = [
        ("src/resoftai", "源代码目录"),
        ("src/resoftai/agents", "智能体目录"),
        ("src/resoftai/api", "API目录"),
        ("src/resoftai/models", "模型目录"),
        ("src/resoftai/orchestration", "工作流目录"),
        ("src/resoftai/plugins", "插件目录"),
        ("tests", "测试目录"),
        ("alembic", "数据库迁移目录"),
        ("requirements.txt", "依赖文件"),
        ("CLAUDE.md", "开发指南"),
    ]

    all_ok = True
    for path, description in required_paths:
        full_path = root / path
        if full_path.exists():
            print_success(f"{description}: {path}")
        else:
            print_error(f"{description}: {path} (不存在)")
            all_ok = False

    return all_ok

def check_models():
    """检查数据模型"""
    print_header("检查数据模型")

    try:
        from resoftai.models import (
            User, Project, File, LLMConfigModel,
            AgentActivity, Task, Log
        )
        print_success("核心模型导入成功")

        # 检查新增的性能监控模型
        from resoftai.models.performance_metrics import (
            WorkflowMetrics, AgentPerformance, SystemMetrics,
            LLMUsageMetrics, PerformanceAlert
        )
        print_success("性能监控模型导入成功")

        return True
    except Exception as e:
        print_error(f"模型导入失败: {e}")
        return False

def check_api_routes():
    """检查API路由"""
    print_header("检查API路由")

    try:
        from resoftai.api import main
        app = main.app

        routes_count = len([r for r in app.routes if hasattr(r, 'methods')])
        print_success(f"API应用导入成功 ({routes_count} 个端点)")

        # 检查关键路由模块
        from resoftai.api.routes import (
            auth, projects, files, execution,
            monitoring, marketplace
        )
        print_success("核心路由模块导入成功")
        print_success("监控路由模块导入成功 (新增)")
        print_success("市场路由模块导入成功 (新增)")

        return True
    except Exception as e:
        print_error(f"API路由检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_agents():
    """检查智能体"""
    print_header("检查AI智能体")

    agents = [
        ("ProjectManagerAgent", "项目经理"),
        ("RequirementsAnalystAgent", "需求分析师"),
        ("ArchitectAgent", "架构师"),
        ("UXUIDesignerAgent", "UI设计师"),
        ("DeveloperAgent", "开发工程师"),
        ("TestEngineerAgent", "测试工程师"),
        ("QualityExpertAgent", "质量专家"),
        ("DevOpsEngineerAgent", "DevOps工程师"),
        ("SecurityExpertAgent", "安全专家"),
        ("PerformanceEngineerAgent", "性能工程师"),
    ]

    all_ok = True
    try:
        from resoftai import agents as agents_module

        for agent_name, description in agents:
            if hasattr(agents_module, agent_name):
                print_success(f"{description} ({agent_name})")
            else:
                print_warning(f"{description} ({agent_name}): 未找到")
                # 不算作严重错误，可能是可选智能体

        return True
    except Exception as e:
        print_error(f"智能体检查失败: {e}")
        return False

def check_workflow():
    """检查工作流引擎"""
    print_header("检查工作流引擎")

    try:
        from resoftai.orchestration.workflow import WorkflowOrchestrator
        print_success("基础工作流引擎导入成功")

        from resoftai.orchestration.optimized_workflow import OptimizedWorkflowOrchestrator
        print_success("优化工作流引擎导入成功 (新增)")

        from resoftai.orchestration.executor import ProjectExecutor
        print_success("项目执行器导入成功")

        return True
    except Exception as e:
        print_error(f"工作流引擎检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_plugins():
    """检查插件系统"""
    print_header("检查插件系统")

    try:
        from resoftai.plugins.manager import PluginManager
        print_success("插件管理器导入成功")

        from resoftai.plugins.marketplace import PluginMarketplace
        print_success("插件市场导入成功 (新增)")

        from resoftai.plugins.hooks import HookManager
        print_success("Hook系统导入成功")

        return True
    except Exception as e:
        print_error(f"插件系统检查失败: {e}")
        return False

def check_database_migrations():
    """检查数据库迁移"""
    print_header("检查数据库迁移")

    root = Path(__file__).parent.parent
    migrations_dir = root / "alembic" / "versions"

    if not migrations_dir.exists():
        print_error("迁移目录不存在")
        return False

    migrations = list(migrations_dir.glob("*.py"))
    migrations = [m for m in migrations if not m.name.startswith("__")]

    print_info(f"找到 {len(migrations)} 个迁移文件:")
    for migration in migrations:
        print_success(f"  - {migration.name}")

    # 检查是否有最新的性能监控迁移
    has_perf_migration = any("performance" in m.name.lower() for m in migrations)
    if has_perf_migration:
        print_success("包含性能监控迁移")
    else:
        print_warning("未找到性能监控迁移")

    return True

def check_tests():
    """检查测试文件"""
    print_header("检查测试文件")

    root = Path(__file__).parent.parent
    tests_dir = root / "tests"

    if not tests_dir.exists():
        print_error("测试目录不存在")
        return False

    test_files = list(tests_dir.rglob("test_*.py"))
    print_info(f"找到 {len(test_files)} 个测试文件")

    # 检查关键测试
    key_tests = [
        "test_workflow.py",
        "test_agents.py",
        "test_optimized_workflow.py",
        "test_performance_monitoring.py",
    ]

    for test in key_tests:
        if any(test in str(f) for f in test_files):
            print_success(f"  - {test}")
        else:
            print_warning(f"  - {test} (未找到)")

    return True

def check_configuration():
    """检查配置"""
    print_header("检查配置")

    root = Path(__file__).parent.parent
    env_file = root / ".env"
    env_example = root / ".env.example"

    if env_file.exists():
        print_success(".env 文件存在")
    else:
        print_warning(".env 文件不存在（使用默认配置）")

    if env_example.exists():
        print_success(".env.example 示例文件存在")
    else:
        print_info(".env.example 示例文件不存在（可选）")

    # 检查必需的环境变量
    required_env_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
    ]

    missing_vars = []
    for var in required_env_vars:
        if var not in os.environ:
            missing_vars.append(var)

    if missing_vars:
        print_warning(f"未设置的环境变量: {', '.join(missing_vars)}")
        print_info("这些变量可以在.env文件中设置或使用默认值")
    else:
        print_success("所有必需环境变量已设置")

    return True

def generate_report(results):
    """生成最终报告"""
    print_header("验证报告")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\n总计检查项: {total}")
    print(f"{Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"{Colors.RED}失败: {failed}{Colors.END}")

    if failed == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'🎉 所有检查项通过！系统可以部署。'.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'=' * 60}{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'⚠️  存在失败项，请检查后再部署。'.center(60)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'=' * 60}{Colors.END}\n")

        print("\n失败的检查项:")
        for check_name, result in results.items():
            if not result:
                print_error(f"  - {check_name}")

        return False

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("ResoftAI 系统验证工具".center(60))
    print("版本: 0.2.2 (Beta)".center(60))
    print("=" * 60)
    print(f"{Colors.END}\n")

    # 执行所有检查
    results = {
        "Python版本": check_python_version(),
        "Python依赖": check_dependencies(),
        "文件结构": check_file_structure(),
        "数据模型": check_models(),
        "API路由": check_api_routes(),
        "AI智能体": check_agents(),
        "工作流引擎": check_workflow(),
        "插件系统": check_plugins(),
        "数据库迁移": check_database_migrations(),
        "测试文件": check_tests(),
        "配置文件": check_configuration(),
    }

    # 生成报告
    success = generate_report(results)

    # 额外建议
    if success:
        print("\n" + "=" * 60)
        print("下一步操作:")
        print("=" * 60)
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置环境: 编辑 .env 文件")
        print("3. 初始化数据库: PYTHONPATH=src alembic upgrade head")
        print("4. 运行测试: PYTHONPATH=src pytest tests/ -v")
        print("5. 启动服务: PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload")
        print("=" * 60 + "\n")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
