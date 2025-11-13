# 多模型支持文档

## 概述

ResoftAI平台现在支持多种大语言模型，用户可以灵活选择使用不同的AI模型提供商。

## 支持的模型

### 1. Anthropic Claude
- **模型**: claude-3-5-sonnet-20241022, claude-3-opus等
- **Provider**: `anthropic`
- **API Base**: 默认官方API

### 2. 智谱AI GLM-4
- **模型**: glm-4-plus, glm-4, glm-4-air等
- **Provider**: `zhipu`
- **API Base**: https://open.bigmodel.cn/api/paas/v4

### 3. DeepSeek
- **模型**: deepseek-chat, deepseek-coder等
- **Provider**: `deepseek`
- **API Base**: https://api.deepseek.com

### 4. Moonshot (Kimi)
- **模型**: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- **Provider**: `moonshot`
- **API Base**: https://api.moonshot.cn/v1

### 5. Minimax
- **模型**: abab6.5-chat, abab6.5s-chat等
- **Provider**: `minimax`
- **API Base**: https://api.minimax.chat/v1

### 6. Google Gemini
- **模型**: gemini-pro, gemini-1.5-pro, gemini-1.5-flash等
- **Provider**: `google`
- **API Base**: https://generativelanguage.googleapis.com/v1beta

## 配置方法

### 方式1: 环境变量配置

编辑 `.env` 文件：

```bash
# 选择模型提供商
LLM_PROVIDER=zhipu  # 或 anthropic, deepseek, moonshot, minimax, google

# API密钥
LLM_API_KEY=your_api_key_here

# 模型名称
LLM_MODEL=glm-4-plus

# 可选: 自定义API Base
LLM_API_BASE=https://custom-api.example.com

# 生成参数
LLM_MAX_TOKENS=8192
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.95
```

### 方式2: 代码配置

```python
from resoftai.llm import LLMFactory, LLMConfig, ModelProvider

# 创建配置
config = LLMConfig(
    provider=ModelProvider.ZHIPU,
    api_key="your_zhipu_api_key",
    model_name="glm-4-plus",
    max_tokens=8192,
    temperature=0.7
)

# 创建提供商实例
llm = LLMFactory.create(config)

# 使用
response = await llm.generate(
    prompt="你好，请介绍一下你自己",
    system_prompt="你是一个helpful助手"
)

print(response.content)
```

### 方式3: CLI参数

```bash
resoftai create "需求描述" \
    --provider zhipu \
    --model glm-4-plus \
    --api-key your_key
```

## 使用示例

### 示例1: 使用智谱GLM-4

```python
import asyncio
from resoftai.llm import LLMFactory, LLMConfig, ModelProvider

async def test_zhipu():
    config = LLMConfig(
        provider=ModelProvider.ZHIPU,
        api_key="your_zhipu_api_key",
        model_name="glm-4-plus"
    )

    llm = LLMFactory.create(config)

    response = await llm.generate(
        prompt="设计一个简单的博客系统",
        system_prompt="你是一个资深的软件架构师"
    )

    print(f"模型: {response.model}")
    print(f"提供商: {response.provider}")
    print(f"Token使用: {response.total_tokens}")
    print(f"回复: {response.content}")

asyncio.run(test_zhipu())
```

### 示例2: 使用DeepSeek

```python
config = LLMConfig(
    provider=ModelProvider.DEEPSEEK,
    api_key="your_deepseek_api_key",
    model_name="deepseek-chat"
)

llm = LLMFactory.create(config)
response = await llm.generate("编写一个Python函数计算斐波那契数列")
```

### 示例3: 使用流式输出

```python
async def test_streaming():
    config = LLMConfig(
        provider=ModelProvider.MOONSHOT,
        api_key="your_moonshot_api_key",
        model_name="moonshot-v1-8k"
    )

    llm = LLMFactory.create(config)

    async for chunk in llm.generate_stream(
        prompt="讲一个故事",
        system_prompt="你是一个故事大师"
    ):
        print(chunk, end="", flush=True)
```

## Agent集成

Agent基类已自动支持多模型：

```python
from resoftai.core.agent import Agent, AgentRole
from resoftai.config.settings import get_settings

class MyAgent(Agent):
    # Agent会自动使用配置的LLM提供商
    pass

# 使用时无需修改代码，只需在配置中指定模型
settings = get_settings()
# settings将读取LLM_PROVIDER等环境变量
```

## 自定义Provider

如果需要添加新的模型提供商：

```python
from resoftai.llm.base import LLMProvider, LLMResponse, LLMConfig

class MyCustomProvider(LLMProvider):
    @property
    def provider_name(self) -> str:
        return "My Custom Provider"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        # 实现生成逻辑
        pass

    async def generate_stream(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        # 实现流式生成
        pass

    def validate_config(self) -> bool:
        # 验证配置
        pass

# 注册自定义提供商
from resoftai.llm import LLMFactory
LLMFactory.register_custom_provider("my_custom", MyCustomProvider)
```

## 模型对比

| 提供商 | 上下文长度 | 推荐场景 | 特点 |
|--------|----------|---------|------|
| Claude | 200K | 复杂推理、长文本 | 最强推理能力 |
| GLM-4 | 128K | 中文任务 | 中文优化 |
| DeepSeek | 32K | 代码生成 | 代码能力强 |
| Kimi | 128K | 长文本分析 | 超长上下文 |
| Minimax | 8K-32K | 对话交互 | 中文对话 |
| Gemini | 1M | 多模态任务 | Google生态 |

## 成本优化

### 建议配置

**开发环境**:
```bash
LLM_PROVIDER=deepseek  # 或其他成本较低的模型
LLM_MODEL=deepseek-chat
```

**生产环境**:
```bash
LLM_PROVIDER=anthropic  # 或根据需求选择
LLM_MODEL=claude-3-5-sonnet-20241022
```

### 按需切换

```python
# 对于简单任务使用轻量模型
simple_config = LLMConfig(
    provider=ModelProvider.DEEPSEEK,
    model_name="deepseek-chat",
    max_tokens=2048
)

# 对于复杂任务使用强大模型
complex_config = LLMConfig(
    provider=ModelProvider.ANTHROPIC,
    model_name="claude-3-5-sonnet-20241022",
    max_tokens=8192
)
```

## 故障排查

### 问题1: API密钥错误

```
AuthenticationError: Invalid API key
```

**解决**: 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确

### 问题2: 模型不存在

```
ValueError: Model not found
```

**解决**: 检查 `LLM_MODEL` 是否为提供商支持的模型名称

### 问题3: API Base错误

```
ConnectionError: Unable to reach API
```

**解决**:
1. 检查网络连接
2. 确认 `LLM_API_BASE` 设置正确
3. 某些提供商可能需要特殊网络配置

## 最佳实践

1. **使用环境变量管理密钥**: 永远不要在代码中硬编码API密钥

2. **根据任务选择模型**:
   - 代码生成 → DeepSeek
   - 中文对话 → GLM-4/Minimax
   - 复杂推理 → Claude
   - 长文本 → Kimi

3. **设置合理的token限制**: 避免不必要的成本

4. **使用流式输出**: 对于长内容生成，提供更好的用户体验

5. **实现重试机制**: 处理API临时故障

6. **监控使用量**: 跟踪token消耗和成本

## 环境变量完整列表

```bash
# 必需
LLM_PROVIDER=anthropic
LLM_API_KEY=your_api_key

# 可选
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_API_BASE=https://custom-api.com
LLM_MAX_TOKENS=8192
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.95

# 向后兼容 (Anthropic)
ANTHROPIC_API_KEY=your_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## 更新日志

- **v0.2.0** (2025-11-13): 添加多模型支持
  - 新增5个模型提供商
  - 统一LLM接口
  - 支持自定义Provider
  - 向后兼容Anthropic配置
