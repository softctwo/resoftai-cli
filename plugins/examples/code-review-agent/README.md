# Code Review Agent Plugin

智能代码审查助手，使用AI自动分析代码质量、安全性和性能。

## 功能特性

- **代码质量分析** - 检查可读性、可维护性和代码异味
- **安全漏洞检测** - 识别SQL注入、XSS等常见安全问题
- **性能优化建议** - 发现性能瓶颈并提供优化方案
- **最佳实践检查** - 验证编码规范和错误处理

## 安装

```bash
# 通过CLI安装
resoftai plugin install code-review-agent

# 或通过Web界面安装
访问 插件市场 -> 搜索 "Code Review Agent" -> 点击安装
```

## 配置

```json
{
  "temperature": 0.3,
  "max_tokens": 2000,
  "review_depth": "standard",
  "focus_areas": ["quality", "security", "performance"]
}
```

### 配置选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | number | 0.3 | LLM温度参数 (0.0-1.0) |
| `max_tokens` | integer | 2000 | 最大输出token数 (100-8000) |
| `review_depth` | string | "standard" | 审查深度: quick/standard/thorough |
| `focus_areas` | array | ["quality", "security"] | 重点审查领域 |

## 使用方法

### API调用

```python
from resoftai.plugins.manager import PluginManager

# 获取插件
plugin = plugin_manager.get_plugin("code-review-agent")

# 审查代码
result = await plugin.review_code(
    code="""
    def get_user(user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return db.execute(query)
    """,
    language="python",
    context_info={"file": "app/models.py"}
)

print(result)
```

### 输出示例

```json
{
  "summary": "代码整体质量良好，发现3个可改进项",
  "issues": [
    {
      "severity": "medium",
      "category": "security",
      "title": "潜在的SQL注入风险",
      "description": "直接拼接SQL查询字符串可能导致SQL注入",
      "line": 2,
      "suggestion": "使用参数化查询或ORM"
    }
  ],
  "metrics": {
    "complexity": 8,
    "maintainability": 72,
    "security_score": 85
  }
}
```

## 开发

```bash
# 克隆仓库
git clone https://github.com/resoftai/plugins/code-review-agent

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/
```

## 许可证

MIT License - 详见 LICENSE 文件

## 支持

- [文档](https://docs.resoftai.com/plugins/code-review-agent)
- [问题反馈](https://github.com/resoftai/plugins/code-review-agent/issues)
- [讨论区](https://github.com/resoftai/plugins/code-review-agent/discussions)
