# ResoftAI 快速开始指南

## 🚀 5分钟快速部署

### 方法一：Docker 一键部署 (推荐)

```bash
# 1. 克隆项目
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 2. 启动开发环境
make dev-docker

# 3. 访问应用
# 前端: http://localhost:5173
# API 文档: http://localhost:8000/docs
```

### 方法二：本地快速安装

```bash
# 1. 克隆项目
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 2. 安装依赖
make install

# 3. 初始化数据库
make db-init

# 4. 启动服务
make dev
```

## 📋 快速验证

### 检查服务状态

```bash
# 健康检查
curl http://localhost:8000/health
# 预期输出: {"status":"healthy","service":"resoftai-api"}

# API 文档
open http://localhost:8000/docs
```

### 默认账户

- **用户名**: `admin`
- **密码**: `admin123`

## 🎯 第一个项目

### 1. 获取访问令牌

```bash
# 登录获取令牌
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. 创建 LLM 配置

```bash
curl -X POST "http://localhost:8000/api/llm-configs" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DeepSeek 配置",
    "provider": "deepseek",
    "api_key": "your-deepseek-api-key",
    "model_name": "deepseek-chat",
    "max_tokens": 4096,
    "temperature": 0.7
  }'
```

### 3. 创建第一个项目

```bash
curl -X POST "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的第一个项目",
    "description": "学习使用 ResoftAI",
    "requirements": "开发一个简单的待办事项应用，支持添加、删除和标记完成任务"
  }'
```

### 4. 启动项目执行

```bash
# 获取项目 ID
PROJECT_ID=$(curl -s "http://localhost:8000/api/projects" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[0].id')

# 启动执行
curl -X POST "http://localhost:8000/api/execution/$PROJECT_ID/start" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. 监控进度

```bash
# 查看执行状态
curl "http://localhost:8000/api/execution/$PROJECT_ID/status" \
  -H "Authorization: Bearer $TOKEN" | jq

# 查看智能体活动
curl "http://localhost:8000/api/agent-activities" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 🔧 环境配置

### 必需的环境变量

创建 `.env` 文件：

```bash
# 复制开发环境配置
cp .env.development .env
```

编辑 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./resoftai.db

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production

# LLM 配置 (至少配置一个)
DEEPSEEK_API_KEY=your-deepseek-api-key
# 或
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 可选配置

```bash
# 日志级别
LOG_LEVEL=DEBUG

# CORS 配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 🛠️ 常用命令

### 开发命令

```bash
# 安装所有依赖
make install

# 启动开发环境
make dev

# 仅启动后端
make dev-backend

# 仅启动前端
make dev-frontend
```

### 测试命令

```bash
# 运行所有测试
make test

# 运行后端测试
make test-backend

# 运行前端测试
make test-frontend

# 代码检查
make lint
```

### 部署命令

```bash
# 开发环境部署
make deploy-dev

# 生产环境部署
make deploy-prod

# Kubernetes 部署
make deploy-k8s
```

## 📊 监控和调试

### 查看日志

```bash
# Docker 环境
docker-compose logs -f backend

# 本地环境
# 查看控制台输出
```

### 系统监控

```bash
# 获取系统指标
curl "http://localhost:8000/api/monitoring/metrics" \
  -H "Authorization: Bearer $TOKEN" | jq

# 重置监控数据
curl -X POST "http://localhost:8000/api/monitoring/reset" \
  -H "Authorization: Bearer $TOKEN"
```

## 🚨 故障排除

### 常见问题

#### 1. 端口被占用

```bash
# 检查端口占用
lsof -i :8000
lsof -i :5173

# 停止占用进程
kill -9 <PID>
```

#### 2. 数据库连接失败

```bash
# 重新初始化数据库
make db-init

# 检查数据库文件
ls -la resoftai.db
```

#### 3. 依赖安装失败

```bash
# 清理并重新安装
make clean
make install
```

#### 4. API 调用失败

```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查认证
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### 获取帮助

- **文档**: 查看 `docs/` 目录
- **API 文档**: http://localhost:8000/docs
- **问题反馈**: GitHub Issues
- **日志文件**: 查看控制台输出或日志文件

## 🎉 下一步

成功运行第一个项目后，你可以：

1. **探索前端界面** - 访问 http://localhost:5173
2. **查看生成的代码** - 在项目文件列表中查看
3. **尝试复杂项目** - 创建更复杂的软件项目
4. **自定义配置** - 调整智能体行为和工作流
5. **部署到生产** - 使用生产环境配置

---

**提示**: 首次使用建议从简单的项目开始，熟悉系统工作流程后再尝试复杂项目。