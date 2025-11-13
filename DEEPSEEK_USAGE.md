# DeepSeek 使用指南

## 快速开始

### 1. 配置DeepSeek

编辑 `.env` 文件，设置DeepSeek作为LLM provider：

```bash
# LLM Provider Configuration
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-5b9262ddae444a629054f94d4f222476
LLM_MODEL=deepseek-chat
LLM_MAX_TOKENS=8192
LLM_TEMPERATURE=0.7
```

### 2. 运行测试

```bash
# 完整集成测试
python test_deepseek.py

# 快速演示
python quick_demo.py

# 实际应用演示（交互式）
python demo_deepseek_development.py
```

## 可用模型

DeepSeek提供以下模型：

- `deepseek-chat` - 通用对话模型（推荐）
- `deepseek-coder` - 专注代码的模型

## 基本使用

### Python代码示例

```python
from resoftai.config import Settings
from resoftai.llm.factory import LLMFactory

# 创建LLM实例
settings = Settings()
llm = LLMFactory.create(settings.get_llm_config())

# 生成回复
response = await llm.generate(
    prompt="写一个快速排序算法",
    system_prompt="你是一个Python专家"
)

print(response.content)
print(f"Token使用: {response.total_tokens}")
```

### 流式响应

```python
# 流式生成
async for chunk in llm.generate_stream(
    prompt="解释什么是微服务架构",
    system_prompt="你是一个架构师"
):
    print(chunk, end="", flush=True)
```

## 在ResoftAI中使用

### CLI方式

```bash
# 使用DeepSeek创建项目
resoftai create \
  --name "我的项目" \
  --requirements "开发一个博客系统"

# 系统会自动使用.env中配置的DeepSeek模型
```

### API方式

```bash
# 启动API服务器
resoftai serve

# 然后通过HTTP API调用
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的项目",
    "requirements": "开发一个博客系统",
    "provider": "deepseek"
  }'
```

## 模型切换

### 临时切换到其他模型

```bash
# 切换到Claude
export LLM_PROVIDER=anthropic
export LLM_API_KEY=your_claude_api_key

# 切换到GLM-4
export LLM_PROVIDER=zhipu
export LLM_API_KEY=your_glm4_api_key

# 切换到Kimi
export LLM_PROVIDER=moonshot
export LLM_API_KEY=your_kimi_api_key
```

### 代码中动态切换

```python
from resoftai.llm.factory import LLMFactory
from resoftai.llm.base import LLMConfig, ModelProvider

# 使用DeepSeek
deepseek_config = LLMConfig(
    provider=ModelProvider.DEEPSEEK,
    api_key="sk-xxx",
    model_name="deepseek-chat"
)
deepseek_llm = LLMFactory.create(deepseek_config)

# 使用GLM-4
glm_config = LLMConfig(
    provider=ModelProvider.ZHIPU,
    api_key="your_glm4_key",
    model_name="glm-4-plus"
)
glm_llm = LLMFactory.create(glm_config)
```

## 最佳实践

### 1. 系统提示词优化

```python
# ✅ 好的系统提示词
system_prompt = """你是一个专业的Python高级工程师。
请编写生产级代码，包含：
- 完整的类型注解
- 详细的文档字符串
- 异常处理
- 遵循PEP8规范"""

# ❌ 不好的系统提示词
system_prompt = "你是程序员"
```

### 2. Token使用优化

```python
# 监控token使用
response = await llm.generate(prompt="...")
print(f"使用了 {response.total_tokens} tokens")

# 对于长文本，使用流式响应
async for chunk in llm.generate_stream(prompt=long_text):
    process(chunk)  # 边生成边处理
```

### 3. 错误处理

```python
try:
    response = await llm.generate(prompt="...")
except Exception as e:
    logger.error(f"LLM调用失败: {e}")
    # 可以尝试降级到其他模型
    fallback_llm = LLMFactory.create(claude_config)
    response = await fallback_llm.generate(prompt="...")
```

### 4. 并发控制

```python
import asyncio
from asyncio import Semaphore

# 限制并发数
sem = Semaphore(5)  # 最多5个并发请求

async def generate_with_limit(prompt):
    async with sem:
        return await llm.generate(prompt=prompt)

# 批量处理
tasks = [generate_with_limit(p) for p in prompts]
results = await asyncio.gather(*tasks)
```

## 常见问题

### Q1: 如何获取DeepSeek API密钥？

访问 [DeepSeek官网](https://www.deepseek.com/) 注册账号并在控制台获取API密钥。

### Q2: DeepSeek支持哪些功能？

- ✅ 文本生成
- ✅ 代码生成
- ✅ 代码审查
- ✅ 翻译
- ✅ 摘要
- ✅ 问答
- ✅ 流式输出

### Q3: Token价格是多少？

请访问DeepSeek官网查看最新定价。一般来说，DeepSeek的价格相比GPT-4和Claude更有竞争力。

### Q4: 遇到503错误怎么办？

503通常是服务暂时不可用，建议：
1. 等待几秒后重试
2. 实现自动重试机制
3. 配置多个provider作为备用

### Q5: DeepSeek vs Claude，如何选择？

**选择DeepSeek**:
- 成本敏感的项目
- 中文内容处理
- 大规模高频调用
- 代码生成任务

**选择Claude**:
- 需要超长上下文
- 复杂推理任务
- 严格安全要求
- 多语言混合场景

### Q6: 可以混合使用多个模型吗？

完全可以！ResoftAI支持在同一项目中使用多个模型：

```python
# 需求分析用Claude（强推理能力）
requirements_llm = LLMFactory.create(claude_config)
requirements = await requirements_llm.generate(...)

# 代码生成用DeepSeek（性价比高）
code_llm = LLMFactory.create(deepseek_config)
code = await code_llm.generate(...)

# 测试用例生成用GLM-4（中文友好）
test_llm = LLMFactory.create(glm_config)
tests = await test_llm.generate(...)
```

## 性能优化建议

### 1. 批处理

```python
# 不好：逐个处理
for item in items:
    result = await llm.generate(prompt=item)
    process(result)

# 好：批量处理
prompts = [create_prompt(item) for item in items]
results = await asyncio.gather(*[
    llm.generate(prompt=p) for p in prompts
])
```

### 2. 缓存结果

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_response(prompt: str):
    # 对于相同的prompt，返回缓存结果
    return asyncio.run(llm.generate(prompt=prompt))
```

### 3. 超时设置

```python
# 在provider中设置超时
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)
```

## 监控和日志

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resoftai")

# 会输出详细的API调用信息
```

### 监控Token使用

```python
total_tokens = 0

async def track_usage(prompt):
    response = await llm.generate(prompt=prompt)
    total_tokens += response.total_tokens
    print(f"累计使用: {total_tokens} tokens")
    return response
```

## 更多资源

- [DeepSeek官方文档](https://www.deepseek.com/docs)
- [ResoftAI多模型支持文档](docs/multi-model-support.md)
- [测试报告](DEEPSEEK_TEST_REPORT.md)

---

**最后更新**: 2025-11-13
