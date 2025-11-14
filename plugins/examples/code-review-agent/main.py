"""
Code Review Agent Plugin

自动代码审查助手，使用AI分析代码质量、安全性和最佳实践。
"""
from typing import Dict, Any, List, Optional
import asyncio
import json

from resoftai.plugins.base import Plugin, PluginMetadata, PluginConfig, PluginContext
from resoftai.core.agent import Agent, AgentRole


class CodeReviewAgent(Plugin):
    """
    智能代码审查Agent插件

    功能：
    - 代码质量分析
    - 安全漏洞检测
    - 性能优化建议
    - 最佳实践检查
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        super().__init__(metadata, config)
        self.agent: Optional[Agent] = None

    def load(self, context: PluginContext) -> bool:
        """加载插件"""
        self.context = context
        context.log_info(f"Loading {self.metadata.name}...")

        try:
            # 验证配置
            if not self.validate_config(self.config.config):
                context.log_error("Invalid configuration")
                return False

            context.log_info(f"{self.metadata.name} loaded successfully")
            return True
        except Exception as e:
            context.log_error(f"Failed to load plugin: {e}")
            return False

    def activate(self) -> bool:
        """激活插件"""
        self.context.log_info(f"Activating {self.metadata.name}...")

        try:
            # 创建Code Review Agent
            self.agent = self._create_agent()

            # 注册到系统
            # 在实际应用中，这里会注册到AgentRegistry

            self.context.log_info(f"{self.metadata.name} activated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to activate plugin: {e}")
            return False

    def deactivate(self) -> bool:
        """停用插件"""
        self.context.log_info(f"Deactivating {self.metadata.name}...")

        try:
            # 清理资源
            self.agent = None

            self.context.log_info(f"{self.metadata.name} deactivated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to deactivate plugin: {e}")
            return False

    def unload(self) -> bool:
        """卸载插件"""
        self.context.log_info(f"Unloading {self.metadata.name}...")

        try:
            # 清理所有资源
            self.agent = None
            self.context = None

            return True
        except Exception as e:
            self.logger.error(f"Failed to unload plugin: {e}")
            return False

    def _create_agent(self) -> Agent:
        """创建Code Review Agent实例"""
        system_prompt = """你是一个专业的代码审查助手。你的职责是：

1. **代码质量分析**
   - 检查代码可读性和可维护性
   - 识别重复代码和代码异味
   - 建议重构机会

2. **安全性检查**
   - 识别常见安全漏洞（SQL注入、XSS等）
   - 检查敏感信息泄露
   - 验证输入验证和数据清理

3. **性能优化**
   - 识别性能瓶颈
   - 建议优化算法和数据结构
   - 检查资源使用效率

4. **最佳实践**
   - 验证编码规范遵守情况
   - 检查错误处理
   - 评估测试覆盖率

请提供详细、可操作的建议，并用Markdown格式输出。
"""

        agent_config = {
            "role": AgentRole.QUALITY_EXPERT,
            "name": "Code Review Assistant",
            "system_prompt": system_prompt,
            "temperature": self.config.get("temperature", 0.3),
            "max_tokens": self.config.get("max_tokens", 2000),
        }

        # 在实际应用中，这里会创建真正的Agent实例
        # agent = Agent(**agent_config)
        # return agent

        # 示例中返回配置
        return agent_config

    async def review_code(self, code: str, language: str, context_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        审查代码

        Args:
            code: 待审查的代码
            language: 编程语言
            context_info: 额外上下文信息

        Returns:
            审查结果
        """
        if not self._active:
            raise RuntimeError("Plugin is not active")

        prompt = f"""请审查以下{language}代码：

```{language}
{code}
```

{f"上下文信息：{json.dumps(context_info, ensure_ascii=False)}" if context_info else ""}

请从代码质量、安全性、性能和最佳实践四个方面进行全面审查。
"""

        # 在实际应用中，这里会调用LLM
        # response = await self.agent.process(prompt)

        # 示例响应
        response = {
            "summary": "代码整体质量良好，发现3个可改进项",
            "issues": [
                {
                    "severity": "medium",
                    "category": "security",
                    "title": "潜在的SQL注入风险",
                    "description": "直接拼接SQL查询字符串可能导致SQL注入",
                    "line": 42,
                    "suggestion": "使用参数化查询或ORM"
                },
                {
                    "severity": "low",
                    "category": "quality",
                    "title": "代码重复",
                    "description": "发现重复的错误处理逻辑",
                    "line": 15,
                    "suggestion": "提取为公共函数"
                },
                {
                    "severity": "low",
                    "category": "performance",
                    "title": "循环中的函数调用",
                    "description": "在循环中重复调用相同的函数",
                    "line": 58,
                    "suggestion": "将结果缓存在循环外"
                }
            ],
            "metrics": {
                "complexity": 8,
                "maintainability": 72,
                "security_score": 85
            }
        }

        return response

    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置Schema"""
        return {
            "type": "object",
            "properties": {
                "temperature": {
                    "type": "number",
                    "default": 0.3,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "LLM温度参数，控制输出随机性"
                },
                "max_tokens": {
                    "type": "integer",
                    "default": 2000,
                    "minimum": 100,
                    "maximum": 8000,
                    "description": "最大输出token数"
                },
                "review_depth": {
                    "type": "string",
                    "enum": ["quick", "standard", "thorough"],
                    "default": "standard",
                    "description": "审查深度级别"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["quality", "security", "performance", "best-practices"]
                    },
                    "default": ["quality", "security"],
                    "description": "重点审查领域"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 简化的验证逻辑
        if "temperature" in config:
            temp = config["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 1:
                return False

        if "max_tokens" in config:
            tokens = config["max_tokens"]
            if not isinstance(tokens, int) or tokens < 100 or tokens > 8000:
                return False

        return True

    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return [
            "code_review",
            "security_analysis",
            "performance_analysis",
            "best_practices_check"
        ]


# 插件入口点
__plugin_class__ = CodeReviewAgent
