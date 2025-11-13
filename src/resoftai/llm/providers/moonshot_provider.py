"""Moonshot (Kimi) provider implementation."""

from typing import Optional
import logging
import httpx

from resoftai.llm.base import LLMProvider, LLMResponse, LLMConfig, ModelProvider

logger = logging.getLogger(__name__)


class MoonshotProvider(LLMProvider):
    """Moonshot AI (Kimi) provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "https://api.moonshot.cn/v1"

    @property
    def provider_name(self) -> str:
        return "Moonshot (Kimi)"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Kimi."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.model_name,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                        "temperature": kwargs.get("temperature", self.config.temperature),
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                provider=ModelProvider.MOONSHOT,
                usage=data.get("usage", {}),
                raw_response=data
            )

        except Exception as e:
            logger.error(f"Moonshot API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Generate streaming response using Kimi."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.config.model_name,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                        "temperature": kwargs.get("temperature", self.config.temperature),
                        "stream": True,
                    },
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                import json
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except:
                                continue

        except Exception as e:
            logger.error(f"Moonshot streaming error: {e}")
            raise

    def validate_config(self) -> bool:
        """Validate Moonshot configuration."""
        if not self.config.api_key:
            return False
        if not self.config.model_name:
            return False
        return True
