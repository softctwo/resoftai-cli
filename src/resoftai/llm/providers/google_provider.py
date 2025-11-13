"""Google Gemini provider implementation."""

from typing import Optional
import logging
import httpx

from resoftai.llm.base import LLMProvider, LLMResponse, LLMConfig, ModelProvider

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.api_base = config.api_base or "https://generativelanguage.googleapis.com/v1beta"

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Gemini."""
        try:
            # Gemini uses a different format
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": system_prompt}]})
                contents.append({"role": "model", "parts": [{"text": "Understood. I'll follow these instructions."}]})

            contents.append({"role": "user", "parts": [{"text": prompt}]})

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/models/{self.config.model_name}:generateContent",
                    params={"key": self.config.api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": contents,
                        "generationConfig": {
                            "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                            "temperature": kwargs.get("temperature", self.config.temperature),
                            "topP": kwargs.get("top_p", self.config.top_p),
                        }
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

            # Extract content from Gemini response
            content = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            content += part["text"]

            # Extract usage info
            usage = {}
            if "usageMetadata" in data:
                metadata = data["usageMetadata"]
                usage = {
                    "prompt_tokens": metadata.get("promptTokenCount", 0),
                    "completion_tokens": metadata.get("candidatesTokenCount", 0),
                    "total_tokens": metadata.get("totalTokenCount", 0),
                }

            return LLMResponse(
                content=content,
                model=self.config.model_name,
                provider=ModelProvider.GOOGLE,
                usage=usage,
                raw_response=data
            )

        except Exception as e:
            logger.error(f"Google Gemini API error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Generate streaming response using Gemini."""
        try:
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": system_prompt}]})
                contents.append({"role": "model", "parts": [{"text": "Understood."}]})

            contents.append({"role": "user", "parts": [{"text": prompt}]})

            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.api_base}/models/{self.config.model_name}:streamGenerateContent",
                    params={"key": self.config.api_key, "alt": "sse"},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": contents,
                        "generationConfig": {
                            "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                            "temperature": kwargs.get("temperature", self.config.temperature),
                        }
                    },
                    timeout=60.0
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                import json
                                data = json.loads(data_str)
                                if "candidates" in data and len(data["candidates"]) > 0:
                                    candidate = data["candidates"][0]
                                    if "content" in candidate and "parts" in candidate["content"]:
                                        for part in candidate["content"]["parts"]:
                                            if "text" in part:
                                                yield part["text"]
                            except:
                                continue

        except Exception as e:
            logger.error(f"Google Gemini streaming error: {e}")
            raise

    def validate_config(self) -> bool:
        """Validate Google Gemini configuration."""
        if not self.config.api_key:
            return False
        if not self.config.model_name:
            return False
        return True
