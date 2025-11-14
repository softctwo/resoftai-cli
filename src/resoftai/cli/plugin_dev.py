"""
Plugin Development CLI

命令行工具用于创建、测试和发布ResoftAI插件
"""
import typer
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
import shutil

app = typer.Typer(help="ResoftAI插件开发工具")


PLUGIN_CATEGORIES = [
    "agent",
    "llm_provider",
    "code_quality",
    "integration",
    "template",
    "generator",
    "workflow",
    "ui",
    "utility"
]


PLUGIN_TEMPLATES = {
    "agent": {
        "description": "AI Agent插件模板",
        "example": "code-review-agent"
    },
    "llm_provider": {
        "description": "LLM提供商插件模板",
        "example": "openai-compatible-provider"
    },
    "code_quality": {
        "description": "代码质量工具插件模板",
        "example": "eslint-integration"
    },
    "integration": {
        "description": "第三方集成插件模板",
        "example": "slack-integration"
    },
    "utility": {
        "description": "通用工具插件模板",
        "example": "markdown-converter"
    }
}


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="插件名称"),
    slug: str = typer.Option(None, "--slug", "-s", help="插件标识符（URL友好）"),
    category: str = typer.Option(..., "--category", "-c", help="插件类别"),
    author: str = typer.Option("Your Name", "--author", "-a", help="作者名称"),
    description: str = typer.Option("", "--description", "-d", help="插件描述"),
    output_dir: Path = typer.Option(Path("plugins"), "--output", "-o", help="输出目录")
):
    """
    创建新的插件项目

    示例:
        resoftai plugin create \\
            --name "My Agent" \\
            --slug my-agent \\
            --category agent \\
            --author "John Doe"
    """
    # 验证类别
    if category not in PLUGIN_CATEGORIES:
        typer.echo(f"❌ 错误: 无效的类别 '{category}'", err=True)
        typer.echo(f"可用类别: {', '.join(PLUGIN_CATEGORIES)}")
        raise typer.Exit(code=1)

    # 生成slug
    if not slug:
        slug = name.lower().replace(" ", "-").replace("_", "-")

    # 创建插件目录
    plugin_dir = output_dir / slug
    if plugin_dir.exists():
        typer.echo(f"❌ 错误: 目录已存在: {plugin_dir}", err=True)
        raise typer.Exit(code=1)

    plugin_dir.mkdir(parents=True)

    typer.echo(f"🚀 创建插件: {name}")
    typer.echo(f"📁 目录: {plugin_dir}")
    typer.echo(f"🏷️  类别: {category}")
    typer.echo()

    # 生成插件文件
    _generate_plugin_manifest(plugin_dir, name, slug, category, author, description)
    _generate_plugin_code(plugin_dir, name, slug, category)
    _generate_readme(plugin_dir, name, slug, category, description)
    _generate_requirements(plugin_dir, category)
    _generate_tests(plugin_dir, name, slug)
    _generate_gitignore(plugin_dir)

    typer.echo("✅ 插件创建成功!")
    typer.echo()
    typer.echo("📝 后续步骤:")
    typer.echo(f"  1. cd {plugin_dir}")
    typer.echo("  2. 编辑 main.py 实现插件逻辑")
    typer.echo("  3. 运行 resoftai plugin test 测试插件")
    typer.echo("  4. 运行 resoftai plugin package 打包插件")
    typer.echo("  5. 运行 resoftai plugin publish 发布到市场")


def _generate_plugin_manifest(
    plugin_dir: Path,
    name: str,
    slug: str,
    category: str,
    author: str,
    description: str
):
    """生成plugin.json"""
    manifest = {
        "name": name,
        "slug": slug,
        "version": "0.1.0",
        "description": description or f"{name} plugin for ResoftAI",
        "author": author,
        "category": category,
        "tags": [category],
        "min_platform_version": "0.2.0",
        "dependencies": [],
        "license": "MIT",
        "homepage": f"https://github.com/your-username/{slug}",
        "documentation": f"https://docs.your-domain.com/plugins/{slug}",
        "repository": f"https://github.com/your-username/{slug}",
        "entry_point": "main.py:{}".format(_to_class_name(slug))
    }

    with open(plugin_dir / "plugin.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    typer.echo(f"  ✓ 创建 plugin.json")


def _generate_plugin_code(plugin_dir: Path, name: str, slug: str, category: str):
    """生成main.py"""
    class_name = _to_class_name(slug)

    template = f'''"""
{name} Plugin

TODO: Add plugin description
"""
from typing import Dict, Any, List, Optional

from resoftai.plugins.base import Plugin, PluginMetadata, PluginConfig, PluginContext


class {class_name}(Plugin):
    """
    {name}

    TODO: Add detailed description
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        super().__init__(metadata, config)
        # TODO: Initialize plugin-specific attributes

    def load(self, context: PluginContext) -> bool:
        """加载插件"""
        self.context = context
        context.log_info(f"Loading {{self.metadata.name}}...")

        try:
            # TODO: Validate configuration
            if not self.validate_config(self.config.config):
                context.log_error("Invalid configuration")
                return False

            # TODO: Initialize resources

            context.log_info(f"{{self.metadata.name}} loaded successfully")
            return True
        except Exception as e:
            context.log_error(f"Failed to load plugin: {{e}}")
            return False

    def activate(self) -> bool:
        """激活插件"""
        self.context.log_info(f"Activating {{self.metadata.name}}...")

        try:
            # TODO: Register hooks, start services, etc.

            self.context.log_info(f"{{self.metadata.name}} activated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to activate plugin: {{e}}")
            return False

    def deactivate(self) -> bool:
        """停用插件"""
        self.context.log_info(f"Deactivating {{self.metadata.name}}...")

        try:
            # TODO: Cleanup resources, unregister hooks, etc.

            self.context.log_info(f"{{self.metadata.name}} deactivated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to deactivate plugin: {{e}}")
            return False

    def unload(self) -> bool:
        """卸载插件"""
        self.context.log_info(f"Unloading {{self.metadata.name}}...")

        try:
            # TODO: Final cleanup

            return True
        except Exception as e:
            self.logger.error(f"Failed to unload plugin: {{e}}")
            return False

    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置Schema"""
        return {{
            "type": "object",
            "properties": {{
                # TODO: Define configuration schema
                "example_option": {{
                    "type": "string",
                    "default": "default_value",
                    "description": "示例配置选项"
                }}
            }}
        }}

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # TODO: Implement configuration validation
        return True

    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return [
            # TODO: List plugin capabilities
            "example_capability"
        ]


# 插件入口点
__plugin_class__ = {class_name}
'''

    with open(plugin_dir / "main.py", "w", encoding="utf-8") as f:
        f.write(template)

    typer.echo(f"  ✓ 创建 main.py")


def _generate_readme(plugin_dir: Path, name: str, slug: str, category: str, description: str):
    """生成README.md"""
    readme = f'''# {name}

{description or f"{name} plugin for ResoftAI"}

## 功能特性

- TODO: 列出主要功能

## 安装

```bash
resoftai plugin install {slug}
```

## 配置

```json
{{
  "example_option": "value"
}}
```

## 使用方法

TODO: 添加使用示例

```python
from resoftai.plugins.manager import PluginManager

# 获取插件
plugin = plugin_manager.get_plugin("{slug}")

# 使用插件功能
# TODO: Add usage examples
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/your-username/{slug}

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/
```

## 许可证

MIT License

## 支持

- [文档](https://docs.your-domain.com/plugins/{slug})
- [问题反馈](https://github.com/your-username/{slug}/issues)
'''

    with open(plugin_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    typer.echo(f"  ✓ 创建 README.md")


def _generate_requirements(plugin_dir: Path, category: str):
    """生成requirements.txt"""
    requirements = [
        "# 插件依赖",
        "# 添加您的依赖项",
    ]

    # 根据类别添加常见依赖
    if category == "llm_provider":
        requirements.append("httpx>=0.24.0")
    elif category == "code_quality":
        requirements.append("# linting tools")

    with open(plugin_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requirements))

    typer.echo(f"  ✓ 创建 requirements.txt")


def _generate_tests(plugin_dir: Path, name: str, slug: str):
    """生成测试文件"""
    tests_dir = plugin_dir / "tests"
    tests_dir.mkdir()

    class_name = _to_class_name(slug)

    test_content = f'''"""
Tests for {name} Plugin
"""
import pytest
from unittest.mock import Mock

from main import {class_name}
from resoftai.plugins.base import PluginMetadata, PluginConfig, PluginContext


@pytest.fixture
def plugin():
    """创建插件实例"""
    metadata = PluginMetadata(
        name="{name}",
        slug="{slug}",
        version="0.1.0",
        description="Test plugin",
        author="Test"
    )
    config = PluginConfig()
    return {class_name}(metadata, config)


@pytest.fixture
def context():
    """创建插件上下文"""
    return PluginContext(
        db_session=Mock(),
        settings=Mock(),
        logger=Mock()
    )


def test_plugin_load(plugin, context):
    """测试插件加载"""
    assert plugin.load(context) == True


def test_plugin_activate(plugin, context):
    """测试插件激活"""
    plugin.load(context)
    assert plugin.activate() == True


def test_plugin_deactivate(plugin, context):
    """测试插件停用"""
    plugin.load(context)
    plugin.activate()
    assert plugin.deactivate() == True


def test_plugin_unload(plugin, context):
    """测试插件卸载"""
    plugin.load(context)
    assert plugin.unload() == True


def test_config_schema(plugin):
    """测试配置Schema"""
    schema = plugin.get_config_schema()
    assert isinstance(schema, dict)
    assert "type" in schema


def test_capabilities(plugin):
    """测试能力列表"""
    capabilities = plugin.get_capabilities()
    assert isinstance(capabilities, list)


# TODO: 添加更多测试
'''

    with open(tests_dir / "test_plugin.py", "w", encoding="utf-8") as f:
        f.write(test_content)

    with open(tests_dir / "__init__.py", "w") as f:
        f.write("")

    typer.echo(f"  ✓ 创建 tests/")


def _generate_gitignore(plugin_dir: Path):
    """生成.gitignore"""
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Distribution
dist/
build/
*.egg-info/
"""

    with open(plugin_dir / ".gitignore", "w") as f:
        f.write(gitignore)

    typer.echo(f"  ✓ 创建 .gitignore")


@app.command()
def test(
    plugin_dir: Path = typer.Argument(Path("."), help="插件目录"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出")
):
    """
    测试插件

    示例:
        resoftai plugin test ./my-plugin
    """
    if not (plugin_dir / "plugin.json").exists():
        typer.echo(f"❌ 错误: 未找到 plugin.json 在 {plugin_dir}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"🧪 测试插件: {plugin_dir.name}")
    typer.echo()

    # 运行pytest
    import subprocess

    cmd = ["pytest", str(plugin_dir / "tests")]
    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        typer.echo()
        typer.echo("✅ 所有测试通过!")
    else:
        typer.echo()
        typer.echo("❌ 测试失败", err=True)
        raise typer.Exit(code=result.returncode)


@app.command()
def validate(
    plugin_dir: Path = typer.Argument(Path("."), help="插件目录")
):
    """
    验证插件配置

    示例:
        resoftai plugin validate ./my-plugin
    """
    manifest_path = plugin_dir / "plugin.json"

    if not manifest_path.exists():
        typer.echo(f"❌ 错误: 未找到 plugin.json", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"🔍 验证插件: {plugin_dir.name}")
    typer.echo()

    # 加载并验证manifest
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)

        # 检查必需字段
        required_fields = ["name", "slug", "version", "description", "author", "category", "entry_point"]
        missing = [field for field in required_fields if field not in manifest]

        if missing:
            typer.echo(f"❌ 缺少必需字段: {', '.join(missing)}", err=True)
            raise typer.Exit(code=1)

        # 检查类别
        if manifest["category"] not in PLUGIN_CATEGORIES:
            typer.echo(f"⚠️  警告: 无效的类别 '{manifest['category']}'")

        # 检查入口点文件
        entry_file = manifest["entry_point"].split(":")[0]
        if not (plugin_dir / entry_file).exists():
            typer.echo(f"❌ 错误: 入口文件不存在: {entry_file}", err=True)
            raise typer.Exit(code=1)

        typer.echo("✅ 插件配置有效!")
        typer.echo()
        typer.echo(f"名称: {manifest['name']}")
        typer.echo(f"版本: {manifest['version']}")
        typer.echo(f"类别: {manifest['category']}")

    except json.JSONDecodeError as e:
        typer.echo(f"❌ 错误: plugin.json 格式无效: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def package(
    plugin_dir: Path = typer.Argument(Path("."), help="插件目录"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件")
):
    """
    打包插件

    示例:
        resoftai plugin package ./my-plugin -o my-plugin-v1.0.0.zip
    """
    if not (plugin_dir / "plugin.json").exists():
        typer.echo(f"❌ 错误: 未找到 plugin.json", err=True)
        raise typer.Exit(code=1)

    # 加载manifest获取版本
    with open(plugin_dir / "plugin.json") as f:
        manifest = json.load(f)

    slug = manifest["slug"]
    version = manifest["version"]

    if not output:
        output = Path(f"{slug}-v{version}.zip")

    typer.echo(f"📦 打包插件: {slug} v{version}")
    typer.echo(f"📁 输出: {output}")
    typer.echo()

    # 创建zip文件
    import zipfile

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in plugin_dir.rglob("*"):
            if file.is_file():
                # 跳过不需要的文件
                if any(skip in str(file) for skip in [".git", "__pycache__", ".pytest_cache", "tests/"]):
                    continue

                arcname = file.relative_to(plugin_dir.parent)
                zipf.write(file, arcname)
                typer.echo(f"  + {arcname}")

    typer.echo()
    typer.echo(f"✅ 打包完成: {output}")
    typer.echo(f"📊 大小: {output.stat().st_size / 1024:.2f} KB")


def _to_class_name(slug: str) -> str:
    """将slug转换为类名"""
    return ''.join(word.capitalize() for word in slug.split('-'))


@app.command()
def list_categories():
    """列出所有可用的插件类别"""
    typer.echo("📋 可用的插件类别:")
    typer.echo()

    for category in PLUGIN_CATEGORIES:
        if category in PLUGIN_TEMPLATES:
            template = PLUGIN_TEMPLATES[category]
            typer.echo(f"  • {category:20} - {template['description']}")
        else:
            typer.echo(f"  • {category}")


if __name__ == "__main__":
    app()
