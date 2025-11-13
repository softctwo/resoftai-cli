"""Anthropic Claude provider implementation."""

from typing import Optional
import logging
from anthropic import Anthropic, AsyncAnthropic

from resoftai.llm.base import LLMProvider, LLMResponse, LLMConfig, ModelProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncAnthropic(api_key=config.api_key)

    @property
    def provider_name(self) -> str:
        return "Anthropic Claude"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Claude."""
        try:
            messages = [{"role": "user", "content": prompt}]

            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                system=system_prompt or "",
                messages=messages
            )

            # Extract text content
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            return LLMResponse(
                content=content,
                model=response.model,
                provider=ModelProvider.ANTHROPIC,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                raw_response=response
            )

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Generate streaming response using Claude."""
        try:
            messages = [{"role": "user", "content": prompt}]

            async with self.client.messages.stream(
                model=self.config.model_name,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                system=system_prompt or "",
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise

    def validate_config(self) -> bool:
        """Validate Anthropic configuration."""
        if not self.config.api_key or self.config.api_key == "your_api_key_here":
            return False
        if not self.config.model_name:
            return False
        return True
