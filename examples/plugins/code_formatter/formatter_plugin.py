"""
Python Code Formatter Plugin

Formats Python code using Black and isort.
"""
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from resoftai.plugins.base import CodeQualityPlugin, PluginMetadata, PluginConfig, PluginContext


class PythonFormatterPlugin(CodeQualityPlugin):
    """
    Plugin to format Python code using Black and isort
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        super().__init__(metadata, config)
        self.black_line_length = config.config.get("black_line_length", 100)
        self.use_isort = config.config.get("use_isort", True)
        self.isort_profile = config.config.get("isort_profile", "black")

    def load(self, context: PluginContext) -> bool:
        """
        Load and initialize the plugin

        Checks if Black and isort are available.
        """
        try:
            # Check if Black is available
            result = subprocess.run(
                ["black", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            self.logger.info(f"Black found: {result.stdout.strip()}")

            # Check if isort is available (if enabled)
            if self.use_isort:
                result = subprocess.run(
                    ["isort", "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.logger.info(f"isort found: {result.stdout.strip()}")

            self.logger.info("Python Code Formatter plugin loaded successfully")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to find required tools: {e}")
            return False
        except FileNotFoundError:
            self.logger.error("Black or isort not installed. Please install: pip install black isort")
            return False

    def activate(self) -> bool:
        """Activate the plugin"""
        self.logger.info("Python Code Formatter plugin activated")
        return True

    def deactivate(self) -> bool:
        """Deactivate the plugin"""
        self.logger.info("Python Code Formatter plugin deactivated")
        return True

    def unload(self) -> bool:
        """Unload the plugin"""
        self.logger.info("Python Code Formatter plugin unloaded")
        return True

    def analyze_code(self, code: str, language: str = "python", file_path: str = None) -> Dict[str, Any]:
        """
        Analyze code and return formatting suggestions

        Args:
            code: Source code to analyze
            language: Programming language (must be 'python')
            file_path: Optional file path

        Returns:
            Analysis results with formatting suggestions
        """
        if language != "python":
            return {
                "language": language,
                "supported": False,
                "message": "This plugin only supports Python code"
            }

        issues = []
        formatted_code = code

        # Format with Black
        try:
            black_result = self._format_with_black(code)
            if black_result != code:
                issues.append({
                    "type": "formatting",
                    "tool": "black",
                    "severity": "info",
                    "message": "Code can be reformatted with Black",
                    "formatted": black_result
                })
                formatted_code = black_result
        except Exception as e:
            self.logger.error(f"Black formatting failed: {e}")
            issues.append({
                "type": "error",
                "tool": "black",
                "severity": "error",
                "message": f"Black formatting error: {str(e)}"
            })

        # Format imports with isort
        if self.use_isort:
            try:
                isort_result = self._format_with_isort(formatted_code)
                if isort_result != formatted_code:
                    issues.append({
                        "type": "formatting",
                        "tool": "isort",
                        "severity": "info",
                        "message": "Imports can be sorted with isort",
                        "formatted": isort_result
                    })
                    formatted_code = isort_result
            except Exception as e:
                self.logger.error(f"isort formatting failed: {e}")
                issues.append({
                    "type": "error",
                    "tool": "isort",
                    "severity": "error",
                    "message": f"isort formatting error: {str(e)}"
                })

        return {
            "language": "python",
            "supported": True,
            "issues": issues,
            "formatted_code": formatted_code,
            "needs_formatting": len(issues) > 0,
            "tools_used": ["black"] + (["isort"] if self.use_isort else [])
        }

    def fix_code(self, code: str, language: str = "python", file_path: str = None) -> str:
        """
        Format code automatically

        Args:
            code: Source code to format
            language: Programming language
            file_path: Optional file path

        Returns:
            Formatted code
        """
        if language != "python":
            return code

        formatted_code = code

        # Apply Black formatting
        try:
            formatted_code = self._format_with_black(formatted_code)
        except Exception as e:
            self.logger.error(f"Black formatting failed: {e}")

        # Apply isort
        if self.use_isort:
            try:
                formatted_code = self._format_with_isort(formatted_code)
            except Exception as e:
                self.logger.error(f"isort formatting failed: {e}")

        return formatted_code

    def _format_with_black(self, code: str) -> str:
        """
        Format code with Black

        Args:
            code: Source code

        Returns:
            Formatted code
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            subprocess.run(
                [
                    "black",
                    "--line-length", str(self.black_line_length),
                    "--quiet",
                    temp_path
                ],
                check=True,
                capture_output=True,
                text=True
            )

            with open(temp_path, 'r') as f:
                formatted = f.read()

            return formatted

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def _format_with_isort(self, code: str) -> str:
        """
        Format imports with isort

        Args:
            code: Source code

        Returns:
            Code with sorted imports
        """
        result = subprocess.run(
            [
                "isort",
                "--profile", self.isort_profile,
                "-"
            ],
            input=code,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            "type": "object",
            "properties": {
                "black_line_length": {
                    "type": "integer",
                    "default": 100,
                    "minimum": 50,
                    "maximum": 200,
                    "description": "Maximum line length for Black formatter"
                },
                "use_isort": {
                    "type": "boolean",
                    "default": True,
                    "description": "Use isort for import sorting"
                },
                "isort_profile": {
                    "type": "string",
                    "enum": ["black", "django", "pycharm", "google"],
                    "default": "black",
                    "description": "isort profile to use"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        if "black_line_length" in config:
            if not isinstance(config["black_line_length"], int):
                return False
            if not (50 <= config["black_line_length"] <= 200):
                return False

        if "isort_profile" in config:
            valid_profiles = ["black", "django", "pycharm", "google"]
            if config["isort_profile"] not in valid_profiles:
                return False

        return True
