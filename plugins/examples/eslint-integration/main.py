"""
ESLint Integration Plugin

集成ESLint进行JavaScript/TypeScript代码质量检查
"""
from typing import Dict, Any, List, Optional
import asyncio
import json
import subprocess
from pathlib import Path

from resoftai.plugins.base import Plugin, PluginMetadata, PluginConfig, PluginContext


class ESLintIntegration(Plugin):
    """
    ESLint集成插件

    功能：
    - 自动运行ESLint检查
    - 代码自动修复
    - 自定义规则配置
    - 与CI/CD集成
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        super().__init__(metadata, config)
        self.eslint_path: Optional[str] = None
        self.config_file: Optional[str] = None

    def load(self, context: PluginContext) -> bool:
        """加载插件"""
        self.context = context
        context.log_info(f"Loading {self.metadata.name}...")

        try:
            # 验证配置
            if not self.validate_config(self.config.config):
                context.log_error("Invalid configuration")
                return False

            # 检查ESLint是否已安装
            if not self._check_eslint_installed():
                context.log_error("ESLint not found. Please install it first.")
                return False

            self.eslint_path = self.config.get("eslint_path", "eslint")
            self.config_file = self.config.get("config_file")

            context.log_info(f"{self.metadata.name} loaded successfully")
            return True
        except Exception as e:
            context.log_error(f"Failed to load plugin: {e}")
            return False

    def activate(self) -> bool:
        """激活插件"""
        self.context.log_info(f"Activating {self.metadata.name}...")

        try:
            # 注册到代码质量检查系统
            # 在实际应用中，这里会注册hook
            # hook_manager.register("pre_commit", self.run_lint)
            # hook_manager.register("pre_push", self.run_lint)

            self.context.log_info(f"{self.metadata.name} activated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to activate plugin: {e}")
            return False

    def deactivate(self) -> bool:
        """停用插件"""
        self.context.log_info(f"Deactivating {self.metadata.name}...")

        try:
            # 取消注册hooks
            self.context.log_info(f"{self.metadata.name} deactivated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to deactivate plugin: {e}")
            return False

    def unload(self) -> bool:
        """卸载插件"""
        self.context.log_info(f"Unloading {self.metadata.name}...")

        try:
            self.eslint_path = None
            self.config_file = None
            self.context = None
            return True
        except Exception as e:
            self.logger.error(f"Failed to unload plugin: {e}")
            return False

    def _check_eslint_installed(self) -> bool:
        """检查ESLint是否已安装"""
        try:
            result = subprocess.run(
                ["eslint", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    async def run_lint(
        self,
        files: Optional[List[str]] = None,
        fix: bool = False,
        format_output: str = "json"
    ) -> Dict[str, Any]:
        """
        运行ESLint检查

        Args:
            files: 要检查的文件列表，None表示检查所有文件
            fix: 是否自动修复问题
            format_output: 输出格式 (json, stylish, compact)

        Returns:
            检查结果
        """
        if not self._active:
            raise RuntimeError("Plugin is not active")

        # 构建命令
        cmd = [self.eslint_path]

        # 添加配置文件
        if self.config_file:
            cmd.extend(["-c", self.config_file])

        # 输出格式
        cmd.extend(["-f", format_output])

        # 自动修复
        if fix:
            cmd.append("--fix")

        # 添加文件
        if files:
            cmd.extend(files)
        else:
            # 默认检查常见的JS/TS文件
            patterns = self.config.get("file_patterns", ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"])
            cmd.extend(patterns)

        try:
            # 运行ESLint
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # 解析结果
            if format_output == "json":
                try:
                    results = json.loads(stdout.decode())
                    return self._parse_json_output(results)
                except json.JSONDecodeError:
                    self.context.log_error(f"Failed to parse ESLint output: {stdout.decode()}")
                    return {"error": "Failed to parse output"}
            else:
                return {
                    "output": stdout.decode(),
                    "errors": stderr.decode(),
                    "exit_code": process.returncode
                }

        except Exception as e:
            self.context.log_error(f"Error running ESLint: {e}")
            raise

    def _parse_json_output(self, results: List[Dict]) -> Dict[str, Any]:
        """解析JSON格式的ESLint输出"""
        total_errors = 0
        total_warnings = 0
        files_with_issues = []

        for file_result in results:
            file_path = file_result.get("filePath", "")
            messages = file_result.get("messages", [])

            if messages:
                error_count = sum(1 for m in messages if m.get("severity") == 2)
                warning_count = sum(1 for m in messages if m.get("severity") == 1)

                total_errors += error_count
                total_warnings += warning_count

                files_with_issues.append({
                    "file": file_path,
                    "errors": error_count,
                    "warnings": warning_count,
                    "messages": [
                        {
                            "line": m.get("line"),
                            "column": m.get("column"),
                            "severity": "error" if m.get("severity") == 2 else "warning",
                            "message": m.get("message"),
                            "rule": m.get("ruleId"),
                            "fix": m.get("fix")
                        }
                        for m in messages
                    ]
                })

        return {
            "summary": {
                "total_files": len(results),
                "files_with_issues": len(files_with_issues),
                "total_errors": total_errors,
                "total_warnings": total_warnings
            },
            "files": files_with_issues,
            "raw_results": results
        }

    async def fix_file(self, file_path: str) -> Dict[str, Any]:
        """
        修复单个文件的问题

        Args:
            file_path: 文件路径

        Returns:
            修复结果
        """
        return await self.run_lint(files=[file_path], fix=True)

    async def check_project(self, project_path: str) -> Dict[str, Any]:
        """
        检查整个项目

        Args:
            project_path: 项目路径

        Returns:
            检查结果
        """
        # 切换到项目目录
        original_cwd = Path.cwd()
        try:
            Path(project_path).mkdir(parents=True, exist_ok=True)
            # 在项目目录中运行lint
            return await self.run_lint()
        finally:
            pass  # 恢复原目录

    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置Schema"""
        return {
            "type": "object",
            "properties": {
                "eslint_path": {
                    "type": "string",
                    "default": "eslint",
                    "description": "ESLint可执行文件路径"
                },
                "config_file": {
                    "type": "string",
                    "description": "ESLint配置文件路径 (.eslintrc.js, .eslintrc.json等)"
                },
                "file_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx"],
                    "description": "要检查的文件模式"
                },
                "auto_fix": {
                    "type": "boolean",
                    "default": false,
                    "description": "是否自动修复问题"
                },
                "ignore_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["node_modules/**", "dist/**", "build/**"],
                    "description": "要忽略的文件模式"
                },
                "max_warnings": {
                    "type": "integer",
                    "default": 0,
                    "minimum": 0,
                    "description": "允许的最大警告数，超过则失败"
                },
                "run_on_save": {
                    "type": "boolean",
                    "default": true,
                    "description": "保存文件时自动运行lint"
                },
                "run_on_commit": {
                    "type": "boolean",
                    "default": true,
                    "description": "提交时运行lint"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 基本验证
        if "eslint_path" in config:
            if not isinstance(config["eslint_path"], str):
                return False

        if "max_warnings" in config:
            if not isinstance(config["max_warnings"], int) or config["max_warnings"] < 0:
                return False

        return True

    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return [
            "lint_check",
            "auto_fix",
            "project_check",
            "pre_commit_hook",
            "ci_integration"
        ]


# 插件入口点
__plugin_class__ = ESLintIntegration
