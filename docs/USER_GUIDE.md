# ResoftAI 用户指南

## 目录

1. [快速开始](#快速开始)
2. [核心概念](#核心概念)
3. [智能体介绍](#智能体介绍)
4. [工作流程](#工作流程)
5. [API 使用](#api-使用)
6. [前端界面](#前端界面)
7. [部署指南](#部署指南)
8. [故障排除](#故障排除)
9. [最佳实践](#最佳实践)

## 快速开始

### 系统要求

- **操作系统**: Linux, macOS, Windows (WSL2)
- **Python**: 3.11 或更高版本
- **Node.js**: 16 或更高版本 (前端开发)
- **数据库**: PostgreSQL 12+ 或 SQLite
- **内存**: 最低 4GB，推荐 8GB
- **存储**: 最低 2GB 可用空间

### 安装步骤

#### 方法一：使用 Docker (推荐)

```bash
# 克隆项目
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 启动开发环境
make dev-docker

# 或启动生产环境
./deploy.sh prod
```

#### 方法二：本地安装

```bash
# 克隆项目
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 安装依赖
make install

# 初始化数据库
make db-init

# 启动开发服务器
make dev
```

### 首次配置

1. **配置环境变量**
   ```bash
   cp .env.development .env
   # 编辑 .env 文件，添加 API 密钥
   ```

2. **创建管理员账户**
   ```bash
   # 系统会自动创建默认管理员账户
   # 用户名: admin
   # 密码: admin123
   ```

3. **配置 LLM 提供商**
   - 访问 http://localhost:8000/docs
   - 使用管理员账户登录
   - 创建 LLM 配置

## 核心概念

### 智能体 (Agents)

ResoftAI 包含 7 个专业智能体，每个智能体负责软件开发流程中的特定任务：

1. **项目经理** - 项目规划和进度管理
2. **需求分析师** - 需求分析和规格说明
3. **软件架构师** - 系统架构设计
4. **UX/UI 设计师** - 用户界面设计
5. **开发工程师** - 代码实现和优化
6. **测试工程师** - 测试用例设计和执行
7. **质量专家** - 质量保证和代码审查

### 工作流 (Workflow)

项目执行遵循 7 阶段工作流：

1. **需求分析** - 分析用户需求，创建需求规格说明书
2. **架构设计** - 设计系统架构和技术栈
3. **UI 设计** - 设计用户界面和交互流程
4. **开发实现** - 编写代码，实现功能
5. **测试验证** - 编写测试用例，验证功能
6. **质量审查** - 代码质量检查和优化
7. **项目完成** - 生成最终交付物

### 项目 (Project)

每个项目包含：
- 项目基本信息
- 需求描述
- 生成的文件和代码
- 执行历史
- 智能体活动记录

## 智能体介绍

### 项目经理 (Project Manager)

**职责**:
- 项目规划和进度跟踪
- 任务分配和协调
- 风险评估和管理
- 项目文档管理

**输出**:
- 项目计划书
- 进度报告
- 风险评估文档

### 需求分析师 (Requirements Analyst)

**职责**:
- 需求收集和分析
- 用户故事编写
- 功能规格定义
- 需求验证

**输出**:
- 需求规格说明书 (SRS)
- 用户故事地图
- 功能需求列表

### 软件架构师 (Software Architect)

**职责**:
- 系统架构设计
- 技术栈选择
- 数据库设计
- 接口设计

**输出**:
- 系统架构文档
- 数据库设计文档
- 技术选型报告

### UX/UI 设计师 (UX/UI Designer)

**职责**:
- 用户界面设计
- 用户体验优化
- 交互流程设计
- 视觉设计规范

**输出**:
- UI 设计稿
- 交互流程图
- 设计规范文档

### 开发工程师 (Developer)

**职责**:
- 代码实现
- 代码质量检查
- 多语言支持
- 最佳实践应用

**输出**:
- 源代码文件
- 代码质量报告
- 部署脚本

### 测试工程师 (Test Engineer)

**职责**:
- 测试用例设计
- 自动化测试
- 缺陷跟踪
- 测试报告

**输出**:
- 测试用例
- 测试报告
- 缺陷报告

### 质量专家 (Quality Expert)

**职责**:
- 代码审查
- 质量评估
- 安全检查
- 性能优化

**输出**:
- 质量评估报告
- 安全审计报告
- 性能优化建议

## 工作流程

### 创建新项目

1. **登录系统**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
   ```

2. **创建项目**
   ```bash
   curl -X POST "http://localhost:8000/api/projects" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "任务管理系统",
       "description": "现代化的任务管理 Web 应用",
       "requirements": "开发一个支持用户注册、任务创建、分配和追踪的 Web 应用"
     }'
   ```

3. **启动项目执行**
   ```bash
   curl -X POST "http://localhost:8000/api/execution/{project_id}/start" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### 监控项目进度

1. **查看执行状态**
   ```bash
   curl "http://localhost:8000/api/execution/{project_id}/status" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **查看智能体活动**
   ```bash
   curl "http://localhost:8000/api/agent-activities" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

3. **查看生成的文件**
   ```bash
   curl "http://localhost:8000/api/files" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### 获取项目成果

1. **下载项目文件**
   ```bash
   curl "http://localhost:8000/api/execution/{project_id}/artifacts" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **查看项目文档**
   - 需求规格说明书
   - 系统设计文档
   - 用户手册
   - 部署指南

## API 使用

### 认证 API

#### 用户注册
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123",
    "full_name": "Test User"
  }'
```

#### 用户登录
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePassword123"
```

### 项目管理 API

#### 获取项目列表
```bash
curl "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 创建项目
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "项目名称",
    "description": "项目描述",
    "requirements": "项目需求"
  }'
```

### 文件管理 API

#### 获取文件列表
```bash
curl "http://localhost:8000/api/files" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 下载文件
```bash
curl "http://localhost:8000/api/files/{file_id}/download" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 监控 API

#### 获取系统指标
```bash
curl "http://localhost:8000/api/monitoring/metrics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 重置监控数据
```bash
curl -X POST "http://localhost:8000/api/monitoring/reset" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 前端界面

### 主要功能

1. **项目管理**
   - 项目列表和详情
   - 项目创建和编辑
   - 项目执行控制

2. **代码编辑器**
   - Monaco Editor 集成
   - 语法高亮
   - 代码补全
   - 多文件编辑

3. **实时监控**
   - 执行进度显示
   - 智能体活动跟踪
   - 系统状态监控

4. **文档查看**
   - 自动生成文档
   - 文档版本历史
   - 文档下载

### 界面布局

- **顶部导航**: 项目切换、用户菜单
- **左侧边栏**: 项目列表、文件树
- **主工作区**: 代码编辑器、文档查看器
- **右侧面板**: 执行状态、智能体活动
- **底部状态栏**: 系统信息、进度指示

## 部署指南

### 开发环境部署

#### 使用 Docker Compose
```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up --build

# 访问应用
# 前端: http://localhost:5173
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

#### 本地开发
```bash
# 安装依赖
make install

# 启动后端
make dev-backend

# 启动前端 (新终端)
make dev-frontend
```

### 生产环境部署

#### 使用 Docker
```bash
# 使用部署脚本
./deploy.sh prod

# 或手动部署
docker-compose up -d
```

#### Kubernetes 部署
```bash
# 前提条件
# - Kubernetes 集群
# - kubectl 配置
# - 容器镜像仓库

# 部署到 Kubernetes
./deploy-k8s.sh
```

### 环境配置

#### 开发环境配置
```bash
cp .env.development .env
# 编辑 .env 文件配置数据库和 API 密钥
```

#### 生产环境配置
```bash
cp .env.production .env
# 编辑 .env 文件配置生产环境参数
```

## 故障排除

### 常见问题

#### 1. 数据库连接失败

**症状**: 应用启动失败，数据库连接错误

**解决方案**:
```bash
# 检查数据库服务状态
docker-compose ps postgres

# 检查数据库连接
python -c "
import asyncio
from resoftai.db import init_db
asyncio.run(init_db())
"
```

#### 2. API 密钥配置错误

**症状**: 智能体无法调用 LLM 服务

**解决方案**:
```bash
# 检查环境变量配置
echo $LLM_API_KEY

# 测试 LLM 连接
curl -X POST "http://localhost:8000/api/llm-configs/{config_id}/test" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. 前端无法连接后端

**症状**: 前端显示连接错误

**解决方案**:
```bash
# 检查后端服务状态
curl http://localhost:8000/health

# 检查 CORS 配置
# 确保前端 URL 在 CORS_ORIGINS 中
```

#### 4. 文件权限问题

**症状**: 文件创建或写入失败

**解决方案**:
```bash
# 检查工作目录权限
ls -la workspace/

# 修复权限
chmod 755 workspace/
```

### 日志查看

#### 查看应用日志
```bash
# Docker 环境
docker-compose logs -f backend

# Kubernetes 环境
kubectl logs -f deployment/backend -n resoftai
```

#### 查看数据库日志
```bash
# Docker 环境
docker-compose logs -f postgres

# Kubernetes 环境
kubectl logs -f statefulset/postgres -n resoftai
```

### 性能优化

#### 内存优化
- 调整 JVM 参数 (如果使用 Java 项目)
- 优化数据库查询
- 启用缓存机制

#### 响应时间优化
- 使用 CDN 加速静态资源
- 启用 Gzip 压缩
- 优化数据库索引

## 最佳实践

### 项目需求编写

#### 好的需求示例
```
开发一个任务管理系统，包含以下功能：
1. 用户注册和登录
2. 任务创建、编辑、删除
3. 任务分配和状态跟踪
4. 用户权限管理
5. 数据导出功能

技术要求：
- 使用 Python FastAPI 后端
- 使用 Vue.js 前端
- 使用 PostgreSQL 数据库
- 支持 Docker 部署
```

#### 避免的需求问题
- 需求过于模糊
- 缺少具体功能描述
- 没有技术栈要求
- 忽略性能和安全要求

### 代码质量保证

#### 启用代码质量检查
- 在项目需求中明确代码质量标准
- 使用多语言代码质量检查
- 定期运行安全扫描

#### 代码审查流程
1. 开发工程师完成代码实现
2. 质量专家进行代码审查
3. 修复发现的问题
4. 重新审查直到通过

### 部署最佳实践

#### 环境分离
- 开发环境: 用于功能开发和测试
- 测试环境: 用于集成测试
- 生产环境: 用于正式部署

#### 备份策略
- 定期备份数据库
- 备份项目文件和配置
- 测试恢复流程

#### 监控告警
- 设置系统监控
- 配置性能告警
- 建立故障响应流程

### 安全最佳实践

#### API 安全
- 使用 HTTPS 加密通信
- 实施 JWT 认证
- 限制 API 访问频率
- 验证输入数据

#### 数据安全
- 加密敏感数据
- 定期更新依赖包
- 实施访问控制
- 审计安全事件

### 性能优化

#### 应用性能
- 启用缓存机制
- 优化数据库查询
- 使用异步处理
- 监控资源使用

#### 部署性能
- 使用多阶段 Docker 构建
- 优化镜像大小
- 配置负载均衡
- 启用自动扩缩容

## 支持与帮助

### 获取帮助

- **文档**: 查看项目 README 和本用户指南
- **API 文档**: 访问 http://localhost:8000/docs
- **问题反馈**: 在 GitHub Issues 提交问题
- **社区支持**: 加入项目社区讨论

### 故障报告

报告问题时请提供：
1. 系统环境信息
2. 错误日志
3. 复现步骤
4. 期望行为
5. 实际行为

### 版本更新

定期检查项目更新：
```bash
git pull origin main
pip install -r requirements.txt
cd frontend && npm install
```

---

**注意**: 本指南基于 ResoftAI v0.2.1 版本编写，具体功能可能随版本更新而变化。