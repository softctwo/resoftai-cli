# ResoftAI插件市场平台完整指南

## 目录

1. [概述](#概述)
2. [插件示例](#插件示例)
3. [开发工具](#开发工具)
4. [API接口](#api接口)
5. [审核流程](#审核流程)
6. [更新机制](#更新机制)
7. [前端集成](#前端集成)
8. [最佳实践](#最佳实践)

---

## 概述

ResoftAI插件市场平台是一个完整的插件生态系统，支持插件的开发、发布、审核、安装和更新。

### 核心功能

- ✅ **插件开发框架** - 完整的插件基础类和生命周期管理
- ✅ **CLI开发工具** - 命令行工具用于创建、测试和打包插件
- ✅ **示例插件** - 3个完整的插件示例（Agent、LLM Provider、代码质量工具）
- ✅ **市场API** - 完整的RESTful API支持浏览、搜索、安装、评价
- ✅ **审核系统** - 自动化检查 + 人工审核workflow
- ✅ **更新通知** - 自动检测插件更新并通知用户
- ✅ **版本管理** - 支持多版本、回滚、兼容性检查
- ✅ **评价系统** - 1-5星评分 + 评论 + 点赞
- ✅ **插件集合** - 用户可创建插件集合列表

### 插件类别

| 类别 | 说明 | 示例 |
|------|------|------|
| `agent` | AI Agent插件 | Code Review Agent |
| `llm_provider` | LLM提供商 | OpenAI Compatible Provider |
| `code_quality` | 代码质量工具 | ESLint Integration |
| `integration` | 第三方集成 | Slack、Jira |
| `template` | 项目模板 | React Template |
| `generator` | 代码生成器 | API Generator |
| `workflow` | 自定义工作流 | CI/CD Workflow |
| `ui` | UI扩展 | Custom Dashboard |
| `utility` | 通用工具 | Markdown Converter |

---

## 插件示例

### 1. Code Review Agent 插件

**位置**: `plugins/examples/code-review-agent/`

**功能**:
- 智能代码审查
- 安全漏洞检测
- 性能优化建议
- 最佳实践检查

**使用示例**:
```python
from resoftai.plugins.manager import PluginManager

# 获取插件
plugin = plugin_manager.get_plugin("code-review-agent")

# 审查代码
result = await plugin.review_code(
    code="def hello(): print('Hello')",
    language="python"
)

print(f"发现 {len(result['issues'])} 个问题")
```

### 2. OpenAI Compatible Provider 插件

**位置**: `plugins/examples/openai-compatible-provider/`

**功能**:
- 支持任何OpenAI兼容API
- 流式响应
- Function Calling
- 多模型支持

**配置示例**:
```json
{
  "api_base": "https://api.openai.com/v1",
  "api_key": "sk-xxx",
  "models": ["gpt-4", "gpt-3.5-turbo"],
  "default_model": "gpt-4"
}
```

### 3. ESLint Integration 插件

**位置**: `plugins/examples/eslint-integration/`

**功能**:
- 自动代码检查
- 自动修复
- Git Hook集成
- CI/CD支持

**使用示例**:
```python
plugin = plugin_manager.get_plugin("eslint-integration")

# 运行lint
result = await plugin.run_lint(fix=True)

print(f"检查了 {result['summary']['total_files']} 个文件")
print(f"发现 {result['summary']['total_errors']} 个错误")
```

---

## 开发工具

### CLI工具

**位置**: `src/resoftai/cli/plugin_dev.py`

#### 创建新插件

```bash
# 创建插件
resoftai plugin create \
  --name "My Agent" \
  --slug my-agent \
  --category agent \
  --author "Your Name"

# 项目结构
my-agent/
├── plugin.json          # 插件清单
├── main.py             # 插件主代码
├── README.md           # 文档
├── requirements.txt    # 依赖
├── .gitignore
└── tests/
    └── test_plugin.py
```

#### 测试插件

```bash
cd my-agent
resoftai plugin test
```

#### 验证插件

```bash
resoftai plugin validate
```

#### 打包插件

```bash
resoftai plugin package -o my-agent-v1.0.0.zip
```

### 插件清单 (plugin.json)

```json
{
  "name": "My Plugin",
  "slug": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Your Name",
  "category": "agent",
  "tags": ["ai", "agent"],
  "min_platform_version": "0.2.0",
  "dependencies": [],
  "license": "MIT",
  "entry_point": "main.py:MyPlugin"
}
```

### 插件基类

```python
from resoftai.plugins.base import Plugin

class MyPlugin(Plugin):
    def load(self, context: PluginContext) -> bool:
        """加载插件"""
        return True

    def activate(self) -> bool:
        """激活插件"""
        return True

    def deactivate(self) -> bool:
        """停用插件"""
        return True

    def unload(self) -> bool:
        """卸载插件"""
        return True

    def get_config_schema(self) -> Dict[str, Any]:
        """配置Schema (JSON Schema格式)"""
        return {}

    def validate_config(self, config: Dict) -> bool:
        """验证配置"""
        return True

    def get_capabilities(self) -> List[str]:
        """插件能力列表"""
        return []
```

---

## API接口

### 浏览市场

```http
GET /api/plugins/marketplace
    ?category=agent
    &search=review
    &sort_by=downloads
    &skip=0
    &limit=20
```

**响应**:
```json
[
  {
    "id": 1,
    "name": "Code Review Agent",
    "slug": "code-review-agent",
    "version": "1.0.0",
    "category": "agent",
    "downloads_count": 1523,
    "rating_average": 4.8,
    "rating_count": 156
  }
]
```

### 搜索插件

```http
GET /api/plugins/marketplace/search?q=review&limit=20
```

### 获取趋势插件

```http
GET /api/plugins/marketplace/trending?days=7&limit=10
```

### 个性化推荐

```http
GET /api/plugins/marketplace/recommended?limit=10
Authorization: Bearer <token>
```

### 安装插件

```http
POST /api/plugins/{plugin_id}/install
Authorization: Bearer <token>

{
  "config": {
    "api_key": "xxx",
    "enabled": true
  }
}
```

### 查看已安装插件

```http
GET /api/plugins/installations
Authorization: Bearer <token>
```

### 卸载插件

```http
DELETE /api/plugins/{plugin_id}/uninstall
Authorization: Bearer <token>
```

### 评价插件

```http
POST /api/plugins/{plugin_id}/reviews
Authorization: Bearer <token>

{
  "rating": 5,
  "title": "Excellent plugin!",
  "content": "Very helpful for code review"
}
```

### 发布插件

```http
POST /api/plugins
Authorization: Bearer <token>

{
  "name": "My Plugin",
  "slug": "my-plugin",
  "version": "1.0.0",
  "category": "agent",
  "description": "...",
  "package_url": "https://...",
  "license": "MIT"
}
```

---

## 审核流程

### 提交审核

```http
POST /api/plugins/{plugin_id}/submit-review
Authorization: Bearer <token>
```

### 自动化检查

**位置**: `src/resoftai/crud/plugin_review.py`

```http
GET /api/plugins/{plugin_id}/automated-checks
Authorization: Bearer <token>
```

**检查项**:
- ✅ 必需字段完整性
- ✅ 版本号格式
- ✅ 描述长度
- ✅ 标签和分类
- ✅ 文档链接
- ✅ 图标
- ✅ 安全检查 (checksum)

**响应**:
```json
{
  "success": true,
  "score": 92.5,
  "can_approve": true,
  "issues_count": 0,
  "warnings_count": 2,
  "issues": [],
  "warnings": [
    {
      "check": "documentation",
      "severity": "warning",
      "message": "建议提供文档链接"
    }
  ],
  "summary": "检查通过（得分: 92.5/100），但有 2 个建议改进项"
}
```

### 人工审核 (管理员)

```http
POST /api/plugins/admin/{plugin_id}/review
Authorization: Bearer <admin_token>

{
  "decision": "approved",  // approved | rejected | needs_changes
  "comments": "Looks good!",
  "required_changes": []
}
```

### 查看待审核列表 (管理员)

```http
GET /api/plugins/admin/pending-reviews?skip=0&limit=20
Authorization: Bearer <admin_token>
```

### 审核统计 (管理员)

```http
GET /api/plugins/admin/review-statistics?days=30
Authorization: Bearer <admin_token>
```

**响应**:
```json
{
  "period_days": 30,
  "pending_review": 15,
  "status_breakdown": {
    "approved": 45,
    "rejected": 5,
    "submitted": 15
  },
  "total_reviewed": 50,
  "approval_rate": 90.0,
  "average_review_time_hours": 24
}
```

---

## 更新机制

### 检查更新

**位置**: `src/resoftai/crud/plugin_updates.py`

```http
GET /api/plugins/updates/check
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_updates": 3,
  "updates": [
    {
      "plugin_id": 1,
      "plugin_name": "Code Review Agent",
      "current_version": "1.0.0",
      "latest_version": "1.2.0",
      "update_type": "minor",  // major | minor | patch
      "is_breaking": false,
      "changelog": [
        {
          "version": "1.2.0",
          "released_at": "2025-01-15T10:00:00Z",
          "changelog": "- Added new features\n- Bug fixes"
        }
      ]
    }
  ]
}
```

### 更新统计

```http
GET /api/plugins/updates/statistics
Authorization: Bearer <token>
```

**响应**:
```json
{
  "total_updates": 3,
  "major_updates": 0,
  "minor_updates": 2,
  "patch_updates": 1,
  "breaking_changes": 0
}
```

### 更新插件

```http
POST /api/plugins/{plugin_id}/update
Authorization: Bearer <token>
```

### 启用自动更新

```http
POST /api/plugins/installations/{installation_id}/auto-update?auto_update=true
Authorization: Bearer <token>
```

---

## 前端集成

### React组件示例

#### 插件市场主页

```typescript
import React from 'react';
import { PluginCard, SearchBar, CategoryFilter } from '@/components';

function PluginMarketplace() {
  const [plugins, setPlugins] = useState([]);
  const [category, setCategory] = useState('all');
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchPlugins();
  }, [category, search]);

  const fetchPlugins = async () => {
    const params = new URLSearchParams({
      category: category !== 'all' ? category : '',
      search,
      sort_by: 'downloads',
      limit: '20'
    });

    const res = await fetch(`/api/plugins/marketplace?${params}`);
    const data = await res.json();
    setPlugins(data);
  };

  return (
    <div className="marketplace">
      <SearchBar onSearch={setSearch} />
      <CategoryFilter value={category} onChange={setCategory} />

      <div className="plugin-grid">
        {plugins.map(plugin => (
          <PluginCard key={plugin.id} plugin={plugin} />
        ))}
      </div>
    </div>
  );
}
```

#### 插件详情页

```typescript
function PluginDetail({ pluginId }) {
  const [plugin, setPlugin] = useState(null);
  const [reviews, setReviews] = useState([]);

  const handleInstall = async () => {
    await fetch(`/api/plugins/${pluginId}/install`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ config: {} })
    });
  };

  return (
    <div className="plugin-detail">
      <h1>{plugin.name}</h1>
      <p>{plugin.description}</p>

      <div className="stats">
        <span>⭐ {plugin.rating_average}</span>
        <span>📥 {plugin.downloads_count} downloads</span>
      </span>

      <button onClick={handleInstall}>Install</button>

      <Reviews reviews={reviews} />
    </div>
  );
}
```

#### 更新通知

```typescript
function UpdateNotification() {
  const [updates, setUpdates] = useState([]);

  useEffect(() => {
    checkUpdates();
  }, []);

  const checkUpdates = async () => {
    const res = await fetch('/api/plugins/updates/check', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    setUpdates(data.updates);
  };

  const handleUpdateAll = async () => {
    for (const update of updates) {
      await fetch(`/api/plugins/${update.plugin_id}/update`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
    }
    checkUpdates();
  };

  if (updates.length === 0) return null;

  return (
    <div className="update-notification">
      <h3>{updates.length} updates available</h3>
      <button onClick={handleUpdateAll}>Update All</button>

      {updates.map(update => (
        <div key={update.plugin_id} className="update-item">
          <span>{update.plugin_name}</span>
          <span>{update.current_version} → {update.latest_version}</span>
          {update.is_breaking && <Badge>Breaking Change</Badge>}
        </div>
      ))}
    </div>
  );
}
```

---

## 最佳实践

### 插件开发

1. **遵循单一职责原则** - 每个插件只做一件事并做好
2. **详细的配置Schema** - 使用JSON Schema定义配置
3. **完整的错误处理** - 捕获并记录所有错误
4. **版本兼容性** - 明确指定平台版本要求
5. **完整的文档** - README、API文档、示例代码
6. **全面的测试** - 单元测试、集成测试

### 发布插件

1. **语义化版本** - 使用 X.Y.Z 格式
2. **详细的Changelog** - 记录每个版本的更改
3. **安全检查** - 提供package checksum
4. **截图和演示** - 展示插件功能
5. **标签优化** - 使用相关的标签提高可发现性

### 维护插件

1. **定期更新** - 跟进平台更新
2. **及时回复** - 处理用户反馈和问题
3. **向后兼容** - 避免破坏性更改
4. **监控性能** - 优化插件性能
5. **安全更新** - 及时修复安全漏洞

---

## 完整技术栈

### 后端
- **语言**: Python 3.11+
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **认证**: JWT
- **缓存**: Redis (可选)

### 前端
- **框架**: React 18+ / Vue 3+
- **状态管理**: Redux / Pinia
- **UI组件**: Ant Design / Material-UI
- **路由**: React Router / Vue Router
- **HTTP客户端**: Axios / Fetch

### 插件系统
- **基类**: Python ABC
- **生命周期**: load → activate → deactivate → unload
- **配置**: JSON Schema
- **Hook系统**: Event-driven
- **依赖管理**: 自动解析和加载

---

## 数据库模型

### Plugin表
```sql
CREATE TABLE plugins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author_id INTEGER,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    downloads_count INTEGER DEFAULT 0,
    rating_average FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### PluginInstallation表
```sql
CREATE TABLE plugin_installations (
    id SERIAL PRIMARY KEY,
    plugin_id INTEGER REFERENCES plugins(id),
    user_id INTEGER REFERENCES users(id),
    installed_version VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    config JSONB,
    installed_at TIMESTAMP DEFAULT NOW()
);
```

### PluginReview表
```sql
CREATE TABLE plugin_reviews (
    id SERIAL PRIMARY KEY,
    plugin_id INTEGER REFERENCES plugins(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(plugin_id, user_id)
);
```

---

## 总结

ResoftAI插件市场平台提供了完整的插件生态系统，包括：

- ✅ 3个完整的示例插件
- ✅ CLI开发工具
- ✅ 自动化审核系统
- ✅ 更新通知机制
- ✅ 完整的REST API
- ✅ 前端集成指南
- ✅ 最佳实践文档

开发者可以轻松创建、发布和维护插件，用户可以方便地浏览、安装和更新插件。

**下一步**:
1. 查看示例插件了解最佳实践
2. 使用CLI工具创建您的第一个插件
3. 参考API文档集成到前端
4. 提交插件到市场供其他用户使用
