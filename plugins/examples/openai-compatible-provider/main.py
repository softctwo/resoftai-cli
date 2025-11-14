"""
OpenAI Compatible Provider Plugin

支持任何OpenAI兼容API的LLM提供商插件
可用于集成：OpenRouter、Together AI、Groq等服务
"""
from typing import Dict, Any, List, Optional, AsyncIterator
import httpx
import json

from resoftai.plugins.base import Plugin, PluginMetadata, PluginConfig, PluginContext
from resoftai.llm.base import BaseLLMProvider, LLMResponse, ChatMessage


class OpenAICompatibleProvider(Plugin, BaseLLMProvider):
    """
    OpenAI兼容API提供商

    支持任何实现OpenAI API规范的服务
    """

    def __init__(self, metadata: PluginMetadata, config: PluginConfig):
        Plugin.__init__(self, metadata, config)
        BaseLLMProvider.__init__(self)
        self.client: Optional[httpx.AsyncClient] = None
        self.api_base: Optional[str] = None
        self.api_key: Optional[str] = None

    def load(self, context: PluginContext) -> bool:
        """加载插件"""
        self.context = context
        context.log_info(f"Loading {self.metadata.name}...")

        try:
            # 验证必需配置
            if not self.validate_config(self.config.config):
                context.log_error("Invalid configuration")
                return False

            self.api_base = self.config.get("api_base")
            self.api_key = self.config.get("api_key")

            if not self.api_base or not self.api_key:
                context.log_error("api_base and api_key are required")
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
            # 创建HTTP客户端
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.config.get("timeout", 60.0)
            )

            # 注册到LLM Factory
            # 在实际应用中，这里会注册到LLMFactory
            # llm_factory.register_provider("openai-compatible", self)

            self.context.log_info(f"{self.metadata.name} activated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to activate plugin: {e}")
            return False

    def deactivate(self) -> bool:
        """停用插件"""
        self.context.log_info(f"Deactivating {self.metadata.name}...")

        try:
            # 清理HTTP客户端
            if self.client:
                # asyncio.run(self.client.aclose())
                self.client = None

            self.context.log_info(f"{self.metadata.name} deactivated successfully")
            return True
        except Exception as e:
            self.context.log_error(f"Failed to deactivate plugin: {e}")
            return False

    def unload(self) -> bool:
        """卸载插件"""
        self.context.log_info(f"Unloading {self.metadata.name}...")

        try:
            self.client = None
            self.api_base = None
            self.api_key = None
            self.context = None
            return True
        except Exception as e:
            self.logger.error(f"Failed to unload plugin: {e}")
            return False

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        调用聊天API

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            LLM响应
        """
        if not self.client:
            raise RuntimeError("Provider is not active")

        # 构建请求
        request_data = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = await self.client.post(
                "/chat/completions",
                json=request_data
            )
            response.raise_for_status()
            data = response.json()

            # 解析响应
            choice = data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "stop")

            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                model=model,
                finish_reason=finish_reason,
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                raw_response=data
            )

        except httpx.HTTPStatusError as e:
            self.context.log_error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.context.log_error(f"Error calling API: {e}")
            raise

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        流式调用聊天API

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Yields:
            文本片段
        """
        if not self.client:
            raise RuntimeError("Provider is not active")

        # 构建请求
        request_data = {
            "model": model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }

        try:
            async with self.client.stream(
                "POST",
                "/chat/completions",
                json=request_data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or line == "data: [DONE]":
                        continue

                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            choice = data["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                yield content

                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            self.context.log_error(f"HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            self.context.log_error(f"Error streaming API: {e}")
            raise

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        # 从配置中读取或返回默认模型
        return self.config.get("models", [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo"
        ])

    def get_config_schema(self) -> Dict[str, Any]:
        """获取配置Schema"""
        return {
            "type": "object",
            "required": ["api_base", "api_key"],
            "properties": {
                "api_base": {
                    "type": "string",
                    "description": "API基础URL",
                    "examples": [
                        "https://api.openai.com/v1",
                        "https://openrouter.ai/api/v1",
                        "https://api.together.xyz/v1"
                    ]
                },
                "api_key": {
                    "type": "string",
                    "description": "API密钥",
                    "format": "password"
                },
                "timeout": {
                    "type": "number",
                    "default": 60.0,
                    "minimum": 1.0,
                    "maximum": 300.0,
                    "description": "请求超时时间（秒）"
                },
                "models": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["gpt-3.5-turbo", "gpt-4"],
                    "description": "可用模型列表"
                },
                "default_model": {
                    "type": "string",
                    "default": "gpt-3.5-turbo",
                    "description": "默认模型"
                },
                "max_retries": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 0,
                    "maximum": 10,
                    "description": "最大重试次数"
                }
            }
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 检查必需字段
        if "api_base" not in config or "api_key" not in config:
            return False

        # 验证API base URL格式
        api_base = config["api_base"]
        if not isinstance(api_base, str) or not api_base.startswith("http"):
            return False

        # 验证API key
        api_key = config["api_key"]
        if not isinstance(api_key, str) or len(api_key) < 10:
            return False

        return True

    def get_capabilities(self) -> List[str]:
        """获取插件能力列表"""
        return [
            "chat",
            "chat_stream",
            "function_calling",
            "vision"  # 如果API支持
        ]


# 插件入口点
__plugin_class__ = OpenAICompatibleProvider
