# OpenAI Compatible Provider Plugin

支持任何OpenAI兼容API的LLM提供商插件，可用于集成OpenRouter、Together AI、Groq等服务。

## 功能特性

- **兼容OpenAI API** - 支持所有遵循OpenAI规范的服务
- **流式响应** - 支持SSE流式输出
- **灵活配置** - 自定义API端点、模型列表等
- **错误重试** - 自动重试失败的请求
- **完整日志** - 详细的调用日志和错误追踪

## 支持的服务

- ✅ OpenAI官方API
- ✅ OpenRouter (多模型路由)
- ✅ Together AI
- ✅ Groq
- ✅ Perplexity AI
- ✅ 其他任何OpenAI兼容服务

## 安装

```bash
resoftai plugin install openai-compatible-provider
```

## 配置

### OpenAI官方

```json
{
  "api_base": "https://api.openai.com/v1",
  "api_key": "sk-xxx",
  "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
  "default_model": "gpt-4-turbo"
}
```

### OpenRouter

```json
{
  "api_base": "https://openrouter.ai/api/v1",
  "api_key": "sk-or-xxx",
  "models": [
    "anthropic/claude-3-opus",
    "google/gemini-pro",
    "meta-llama/llama-3-70b"
  ],
  "default_model": "anthropic/claude-3-opus"
}
```

### Together AI

```json
{
  "api_base": "https://api.together.xyz/v1",
  "api_key": "xxx",
  "models": [
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "meta-llama/Llama-3-70b-chat-hf"
  ]
}
```

### Groq

```json
{
  "api_base": "https://api.groq.com/openai/v1",
  "api_key": "gsk_xxx",
  "models": ["llama3-70b-8192", "mixtral-8x7b-32768"],
  "timeout": 30.0
}
```

## 使用方法

### Python API

```python
from resoftai.plugins.manager import PluginManager
from resoftai.llm.base import ChatMessage

# 获取提供商
provider = plugin_manager.get_plugin("openai-compatible-provider")

# 普通调用
messages = [
    ChatMessage(role="user", content="解释什么是量子计算")
]

response = await provider.chat(
    messages=messages,
    model="gpt-4-turbo",
    temperature=0.7,
    max_tokens=1000
)

print(response.content)
```

### 流式调用

```python
# 流式响应
async for chunk in provider.chat_stream(
    messages=messages,
    model="gpt-4-turbo"
):
    print(chunk, end="", flush=True)
```

### 在Agent中使用

```python
from resoftai.core.agent import Agent

# 创建使用该提供商的Agent
agent = Agent(
    role="developer",
    llm_provider="openai-compatible-provider",
    llm_model="gpt-4-turbo"
)

result = await agent.process("帮我写一个Python排序算法")
```

## 配置选项

| 选项 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `api_base` | string | ✅ | - | API基础URL |
| `api_key` | string | ✅ | - | API密钥 |
| `timeout` | number | ❌ | 60.0 | 请求超时（秒） |
| `models` | array | ❌ | - | 可用模型列表 |
| `default_model` | string | ❌ | gpt-3.5-turbo | 默认模型 |
| `max_retries` | integer | ❌ | 3 | 最大重试次数 |

## 高级功能

### 自定义请求头

```python
# 通过kwargs传递自定义参数
response = await provider.chat(
    messages=messages,
    model="gpt-4",
    HTTP_Referer="https://your-app.com",  # OpenRouter需要
    X_Title="Your App Name"  # OpenRouter需要
)
```

### Function Calling

```python
# 如果API支持function calling
response = await provider.chat(
    messages=messages,
    model="gpt-4",
    functions=[{
        "name": "get_weather",
        "description": "获取天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }]
)
```

## 故障排除

### 连接超时

增加timeout配置：
```json
{
  "timeout": 120.0
}
```

### API限流

配置重试参数：
```json
{
  "max_retries": 5
}
```

### 不支持的模型

检查模型名称是否正确，参考服务商文档。

## 开发

```bash
# 克隆仓库
git clone https://github.com/resoftai/plugins/openai-compatible-provider

# 安装依赖
pip install httpx

# 运行测试
pytest tests/
```

## 许可证

MIT License

## 相关链接

- [OpenAI API文档](https://platform.openai.com/docs/api-reference)
- [OpenRouter文档](https://openrouter.ai/docs)
- [Together AI文档](https://docs.together.ai/)
- [Groq文档](https://console.groq.com/docs)
