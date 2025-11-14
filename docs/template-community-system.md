# ResoftAI 模板社区系统

**版本**: 1.0
**创建日期**: 2025-11-14
**状态**: ✅ 后端完成，前端待实现

---

## 📋 概述

模板社区系统将 ResoftAI 从静态模板库升级为一个完整的社区驱动平台，允许用户：
- ✅ 创建和贡献自己的项目模板
- ✅ 对模板进行评分和评论
- ✅ 创建私有模板（仅自己可见）
- ✅ 管理模板的多个版本

---

## 🎯 核心功能

### 1. 模板贡献系统

用户可以创建和发布自己的项目模板。

**功能特性**:
- ✅ 创建草稿模板
- ✅ 添加模板内容（变量、文件、目录）
- ✅ 发布模板到社区
- ✅ 更新已发布的模板
- ✅ 归档或删除模板

**工作流程**:
```
1. 创建模板 (status=draft)
2. 添加版本 (version 1.0.0)
3. 测试和完善
4. 发布模板 (status=published)
5. 用户下载和使用
```

### 2. 模板评分和评论

用户可以对使用过的模板进行评价。

**评分系统**:
- 1-5星评分
- 可选的文字评论
- 平均评分自动计算
- 评分数量统计

**评论系统**:
- 发表评论
- 回复评论（支持嵌套）
- 编辑自己的评论
- 删除评论（软删除）
- 评论点赞功能

### 3. 私有模板支持

用户可以创建仅自己可见的私有模板。

**可见性级别**:
- `PUBLIC`: 所有用户可见
- `PRIVATE`: 仅作者可见
- `ORGANIZATION`: 组织成员可见（预留）

**权限控制**:
- 公开模板：所有人可查看，仅作者可编辑
- 私有模板：仅作者可查看和编辑
- 评论和评分：需要登录

### 4. 模板版本管理

每个模板可以有多个版本，支持版本历史和回溯。

**版本特性**:
- 语义化版本号（1.0.0, 1.1.0, 2.0.0）
- 版本变更日志
- 标记稳定版本
- 自动标记最新版本
- 版本内容完整记录

**版本信息**:
- 版本号和名称
- 创建时间和作者
- 变更说明
- 模板内容（变量、文件、目录）
- 依赖要求

---

## 🗄️ 数据库架构

### 表结构

#### 1. `templates` - 模板主表
```sql
id                INT PRIMARY KEY
template_id       VARCHAR(100) UNIQUE  -- 模板唯一标识符
name              VARCHAR(200)         -- 显示名称
description       TEXT                 -- 详细描述
category          VARCHAR(50)          -- 类别
author_id         INT FK(users.id)     -- 作者
visibility        ENUM                 -- 可见性
status            ENUM                 -- 状态
tags              JSON                 -- 标签
icon_url          VARCHAR(500)         -- 图标URL
screenshot_urls   JSON                 -- 截图URLs
download_count    INT                  -- 下载次数
usage_count       INT                  -- 使用次数
view_count        INT                  -- 浏览次数
average_rating    FLOAT                -- 平均评分
rating_count      INT                  -- 评分数量
current_version_id INT FK(template_versions.id)
created_at        DATETIME
updated_at        DATETIME
published_at      DATETIME
```

#### 2. `template_versions` - 模板版本表
```sql
id                INT PRIMARY KEY
template_id       INT FK(templates.id)
version           VARCHAR(50)          -- 版本号 (1.0.0)
version_name      VARCHAR(200)         -- 版本名称
changelog         TEXT                 -- 变更日志
variables         JSON                 -- 变量定义
files             JSON                 -- 文件列表
directories       JSON                 -- 目录结构
setup_commands    JSON                 -- 安装命令
requirements      JSON                 -- 依赖要求
dependencies      JSON                 -- 依赖包
is_stable         BOOLEAN              -- 是否稳定版
is_latest         BOOLEAN              -- 是否最新版
created_at        DATETIME
created_by_id     INT FK(users.id)

UNIQUE(template_id, version)
```

#### 3. `template_ratings` - 模板评分表
```sql
id                INT PRIMARY KEY
template_id       INT FK(templates.id)
user_id           INT FK(users.id)
rating            INT (1-5)            -- 评分
review            TEXT                 -- 评论文字
helpful_count     INT                  -- 点赞数
created_at        DATETIME
updated_at        DATETIME

UNIQUE(template_id, user_id)
```

#### 4. `template_comments` - 模板评论表
```sql
id                INT PRIMARY KEY
template_id       INT FK(templates.id)
user_id           INT FK(users.id)
content           TEXT                 -- 评论内容
parent_id         INT FK(template_comments.id) -- 父评论ID
is_edited         BOOLEAN              -- 是否已编辑
is_deleted        BOOLEAN              -- 是否已删除
helpful_count     INT                  -- 点赞数
created_at        DATETIME
updated_at        DATETIME
```

#### 5. `template_likes` - 模板收藏表
```sql
id                INT PRIMARY KEY
template_id       INT FK(templates.id)
user_id           INT FK(users.id)
created_at        DATETIME

UNIQUE(template_id, user_id)
```

### 索引设计

```sql
-- 性能优化索引
idx_template_author_status(author_id, status)
idx_template_category_status(category, status)
idx_template_visibility_status(visibility, status)
idx_template_version_latest(template_id, is_latest)
idx_template_rating_score(template_id, rating)
idx_template_comment_created(template_id, created_at)
```

---

## 🔌 API 端点

### 模板管理

#### 创建模板
```http
POST /api/v1/community/templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": "my-custom-template",
  "name": "My Custom Template",
  "description": "A template for...",
  "category": "web_app",
  "visibility": "public",
  "tags": ["fastapi", "vue3", "docker"]
}
```

#### 列出模板
```http
GET /api/v1/community/templates?category=web_app&tags=fastapi,docker&sort_by=rating&limit=20

Response:
{
  "templates": [...],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

#### 获取模板详情
```http
GET /api/v1/community/templates/{template_id}

Response:
{
  "id": 1,
  "template_id": "my-custom-template",
  "name": "My Custom Template",
  "average_rating": 4.5,
  "rating_count": 23,
  ...
}
```

#### 更新模板
```http
PUT /api/v1/community/templates/{template_id}
Authorization: Bearer <token>

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### 发布模板
```http
POST /api/v1/community/templates/{template_id}/publish
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "status": "published",
  "published_at": "2025-11-14T10:00:00Z"
}
```

#### 删除模板
```http
DELETE /api/v1/community/templates/{template_id}
Authorization: Bearer <token>
```

### 版本管理

#### 创建新版本
```http
POST /api/v1/community/templates/{template_id}/versions
Authorization: Bearer <token>

{
  "version": "1.1.0",
  "version_name": "Feature Update",
  "changelog": "Added new features...",
  "variables": [...],
  "files": [...],
  "directories": [...],
  "is_stable": true
}
```

#### 列出所有版本
```http
GET /api/v1/community/templates/{template_id}/versions

Response:
[
  {
    "id": 2,
    "version": "1.1.0",
    "is_latest": true,
    "is_stable": true,
    ...
  },
  {
    "id": 1,
    "version": "1.0.0",
    "is_latest": false,
    "is_stable": true,
    ...
  }
]
```

#### 获取特定版本
```http
GET /api/v1/community/templates/{template_id}/versions/1.0.0

Response:
{
  "version": "1.0.0",
  "variables": [...],
  "files": [...],
  "directories": [...],
  ...
}
```

### 评分和评论

#### 添加/更新评分
```http
POST /api/v1/community/templates/{template_id}/ratings
Authorization: Bearer <token>

{
  "rating": 5,
  "review": "Excellent template! Very helpful."
}
```

#### 列出评分
```http
GET /api/v1/community/templates/{template_id}/ratings?skip=0&limit=20

Response:
{
  "ratings": [...],
  "total": 23,
  "skip": 0,
  "limit": 20
}
```

#### 添加评论
```http
POST /api/v1/community/templates/{template_id}/comments
Authorization: Bearer <token>

{
  "content": "Great template!",
  "parent_id": null  // or comment_id for replies
}
```

#### 列出评论
```http
GET /api/v1/community/templates/{template_id}/comments?skip=0&limit=50

Response:
{
  "comments": [...],
  "total": 45,
  "skip": 0,
  "limit": 50
}
```

#### 更新评论
```http
PUT /api/v1/community/templates/comments/{comment_id}
Authorization: Bearer <token>

{
  "content": "Updated comment"
}
```

#### 删除评论
```http
DELETE /api/v1/community/templates/comments/{comment_id}
Authorization: Bearer <token>
```

### 收藏功能

#### 收藏/取消收藏
```http
POST /api/v1/community/templates/{template_id}/like
Authorization: Bearer <token>

Response:
{
  "liked": true,
  "message": "Template liked"
}
```

#### 获取收藏列表
```http
GET /api/v1/community/templates/liked
Authorization: Bearer <token>

Response:
{
  "templates": [...],
  "total": 10,
  ...
}
```

#### 获取我的模板
```http
GET /api/v1/community/templates/my-templates?status=published
Authorization: Bearer <token>

Response:
{
  "templates": [...],
  "total": 5,
  ...
}
```

---

## 💻 使用示例

### Python 客户端示例

```python
import httpx

API_BASE = "http://localhost:8000/api/v1/community/templates"
TOKEN = "your-jwt-token"

# 创建模板
async def create_template():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_BASE,
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "template_id": "fastapi-microservice",
                "name": "FastAPI Microservice",
                "description": "Production-ready FastAPI microservice template",
                "category": "microservice",
                "tags": ["fastapi", "docker", "postgresql"]
            }
        )
        return response.json()

# 添加版本
async def add_version(template_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/{template_id}/versions",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "version": "1.0.0",
                "variables": [
                    {
                        "name": "service_name",
                        "type": "string",
                        "description": "Service name",
                        "required": True
                    }
                ],
                "files": [
                    {
                        "path": "main.py",
                        "content": "from fastapi import FastAPI\n...",
                        "is_template": True
                    }
                ],
                "directories": ["app", "tests", "docker"],
                "is_stable": True
            }
        )
        return response.json()

# 发布模板
async def publish(template_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/{template_id}/publish",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        return response.json()

# 搜索模板
async def search_templates(query):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            API_BASE,
            params={
                "search": query,
                "sort_by": "rating",
                "limit": 20
            }
        )
        return response.json()

# 评分
async def rate_template(template_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/{template_id}/ratings",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "rating": 5,
                "review": "Excellent template!"
            }
        )
        return response.json()
```

---

## 🎨 前端集成（待实现）

### 需要的Vue组件

#### 1. 模板创建/编辑器
```vue
<!-- TemplateEditor.vue -->
<template>
  <el-form>
    <el-form-item label="Template ID">
      <el-input v-model="template.template_id" />
    </el-form-item>
    <el-form-item label="Name">
      <el-input v-model="template.name" />
    </el-form-item>
    <!-- ... -->
  </el-form>
</template>
```

#### 2. 模板列表（社区）
```vue
<!-- TemplateCommunity.vue -->
<template>
  <div>
    <!-- 搜索和过滤 -->
    <el-row>
      <el-input v-model="search" placeholder="Search templates..." />
      <el-select v-model="category">
        <el-option label="All" value="" />
        <!-- ... -->
      </el-select>
    </el-row>

    <!-- 模板网格 -->
    <el-row :gutter="20">
      <el-col v-for="template in templates" :key="template.id">
        <TemplateCard :template="template" />
      </el-col>
    </el-row>
  </div>
</template>
```

#### 3. 模板详情
```vue
<!-- TemplateDetail.vue -->
<template>
  <div>
    <!-- 模板信息 -->
    <h1>{{ template.name }}</h1>
    <el-rate v-model="template.average_rating" disabled />
    <p>{{ template.description }}</p>

    <!-- 版本选择 -->
    <el-select v-model="selectedVersion">
      <el-option v-for="v in versions" :label="v.version" :value="v.version" />
    </el-select>

    <!-- 评分和评论 -->
    <RatingList :template-id="template.id" />
    <CommentList :template-id="template.id" />
  </div>
</template>
```

#### 4. 评分组件
```vue
<!-- RatingSection.vue -->
<template>
  <div>
    <h3>Rate this template</h3>
    <el-rate v-model="rating" />
    <el-input v-model="review" type="textarea" placeholder="Write a review..." />
    <el-button @click="submitRating">Submit Rating</el-button>
  </div>
</template>
```

#### 5. 评论组件
```vue
<!-- CommentSection.vue -->
<template>
  <div>
    <h3>Comments</h3>
    <CommentItem v-for="comment in comments" :key="comment.id" :comment="comment" />
    <el-input v-model="newComment" placeholder="Add a comment..." />
    <el-button @click="postComment">Post</el-button>
  </div>
</template>
```

---

## 🔐 权限控制

### 权限矩阵

| 操作 | 公开用户 | 已登录用户 | 模板作者 | 管理员 |
|------|---------|-----------|---------|--------|
| 查看公开模板 | ✅ | ✅ | ✅ | ✅ |
| 查看私有模板 | ❌ | 仅自己 | ✅ | ✅ |
| 创建模板 | ❌ | ✅ | ✅ | ✅ |
| 编辑模板 | ❌ | 仅自己 | ✅ | ✅ |
| 删除模板 | ❌ | 仅自己 | ✅ | ✅ |
| 发布模板 | ❌ | 仅自己 | ✅ | ✅ |
| 创建版本 | ❌ | 仅作者 | ✅ | ✅ |
| 评分 | ❌ | ✅ | ✅ | ✅ |
| 评论 | ❌ | ✅ | ✅ | ✅ |
| 编辑评论 | ❌ | 仅自己 | 仅自己 | ✅ |
| 删除评论 | ❌ | 仅自己 | 仅自己 | ✅ |
| 收藏模板 | ❌ | ✅ | ✅ | ✅ |

---

## 📈 统计和分析

### 模板统计信息

每个模板自动追踪：
- **浏览次数** (`view_count`)
- **下载次数** (`download_count`)
- **使用次数** (`usage_count`)
- **平均评分** (`average_rating`)
- **评分数量** (`rating_count`)

### 排序选项

模板列表支持多种排序：
- 最新创建 (`created_at DESC`)
- 最近更新 (`updated_at DESC`)
- 最高评分 (`average_rating DESC`)
- 最多下载 (`download_count DESC`)

---

## 🚀 下一步计划

### Phase 1: 前端实现（待完成）
- [ ] 创建模板编辑器组件
- [ ] 创建社区模板浏览界面
- [ ] 实现评分和评论UI
- [ ] 添加模板收藏功能
- [ ] 实现"我的模板"管理页面

### Phase 2: 增强功能
- [ ] 模板搜索优化（全文搜索）
- [ ] 模板依赖检查
- [ ] 模板预览功能
- [ ] 模板导入/导出
- [ ] 模板Fork功能

### Phase 3: 社区运营
- [ ] 模板审核机制
- [ ] 举报和内容审查
- [ ] 用户信誉系统
- [ ] 模板推荐算法
- [ ] 热门模板榜单

### Phase 4: 高级功能
- [ ] 组织模板（团队共享）
- [ ] 模板市场（付费模板）
- [ ] 模板分析和洞察
- [ ] API使用统计
- [ ] 模板使用报告

---

## 🔧 开发指南

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "Add template community tables"

# 运行迁移
alembic upgrade head
```

### 注册API路由

在 `src/resoftai/api/main.py` 中注册路由：

```python
from resoftai.api.routes import template_community

app.include_router(template_community.router)
```

### 测试API

```bash
# 启动服务器
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload

# 访问API文档
open http://localhost:8000/docs

# 测试创建模板
curl -X POST http://localhost:8000/api/v1/community/templates \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "test-template",
    "name": "Test Template",
    "description": "A test template",
    "category": "web_app"
  }'
```

---

## 📚 参考资源

### 相关文档
- [模板系统设计](./template-system-design.md)
- [API文档](http://localhost:8000/docs)
- [数据库模型](../src/resoftai/models/template_community.py)

### 类似系统参考
- [GitHub Templates](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [Yeoman](https://yeoman.io/)
- [Cookiecutter](https://cookiecutter.readthedocs.io/)

---

**文档版本**: 1.0
**最后更新**: 2025-11-14
**维护者**: Claude
**状态**: ✅ 后端完成，前端待实现
