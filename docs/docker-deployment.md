# ResoftAI Docker 部署指南

**版本**: 1.0
**更新日期**: 2025-11-14
**适用范围**: ResoftAI v0.2.0+

---

## 📋 目录

1. [快速开始](#快速开始)
2. [环境要求](#环境要求)
3. [开发环境部署](#开发环境部署)
4. [生产环境部署](#生产环境部署)
5. [配置说明](#配置说明)
6. [常用命令](#常用命令)
7. [故障排查](#故障排查)
8. [备份和恢复](#备份和恢复)

---

## 🚀 快速开始

### 一键启动（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/softctwo/resoftai-cli.git
cd resoftai-cli

# 2. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置文件

# 3. 启动开发环境
./scripts/docker-start.sh dev

# 或启动生产环境
./scripts/docker-start.sh prod
```

### 访问地址

**开发环境**:
- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

**生产环境**:
- 应用入口: http://localhost (或配置的域名)
- 所有请求通过 Nginx 代理

---

## 💻 环境要求

### 系统要求

- **操作系统**: Linux, macOS, Windows (with WSL2)
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **磁盘空间**: 最少 5GB 可用空间
- **内存**: 最少 4GB RAM (推荐 8GB+)

### 安装 Docker

**Ubuntu/Debian**:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**macOS**:
```bash
brew install --cask docker
```

**Windows**:
下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 验证安装

```bash
docker --version
docker-compose --version
```

---

## 🛠️ 开发环境部署

### 架构概览

开发环境包含以下服务：

```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │
│  (Node.js)  │     │  (Uvicorn)  │
│  Port 5173  │     │  Port 8000  │
└─────────────┘     └──────┬──────┘
                           │
                   ┌───────┴───────┐
                   │               │
              ┌────▼─────┐   ┌────▼────┐
              │ Postgres │   │  Redis  │
              │ Port 5432│   │Port 6379│
              └──────────┘   └─────────┘
```

### 步骤 1: 准备环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要参数：

```bash
# 数据库配置
DB_NAME=resoftai
DB_USER=resoftai
DB_PASSWORD=resoftai123
POSTGRES_PORT=5432

# Redis配置
REDIS_PASSWORD=redis123
REDIS_PORT=6379

# JWT配置（开发环境可使用默认值）
JWT_SECRET_KEY=dev-secret-key-not-for-production

# LLM API密钥（至少配置一个）
DEEPSEEK_API_KEY=your-deepseek-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# OPENAI_API_KEY=your-openai-api-key

# CORS（开发环境）
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
```

### 步骤 2: 启动服务

使用启动脚本：

```bash
./scripts/docker-start.sh dev
```

或手动启动：

```bash
docker-compose up --build -d
```

### 步骤 3: 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 测试后端健康
curl http://localhost:8000/health

# 访问前端
open http://localhost:5173
```

### 开发模式特性

- ✅ **热重载**: 代码修改自动生效
- ✅ **源码挂载**: 本地代码实时同步到容器
- ✅ **开发工具**: 包含调试工具和详细日志
- ✅ **快速启动**: 优化的构建缓存

---

## 🏭 生产环境部署

### 架构概览

生产环境使用 Nginx 作为反向代理：

```
            ┌─────────────┐
            │    Nginx    │
            │   Port 80   │
            └──────┬──────┘
                   │
       ┌───────────┴───────────┐
       │                       │
  ┌────▼─────┐          ┌─────▼────┐
  │ Frontend │          │  Backend │
  │  (静态)  │          │(Gunicorn)│
  └──────────┘          └─────┬────┘
                              │
                      ┌───────┴───────┐
                      │               │
                 ┌────▼─────┐   ┌────▼────┐
                 │ Postgres │   │  Redis  │
                 └──────────┘   └─────────┘
```

### 步骤 1: 准备生产环境变量

**重要**: 生产环境必须使用安全的配置！

```bash
cp .env.example .env
nano .env
```

**必须修改的配置**:

```bash
# 强密码配置
DB_PASSWORD=<使用强密码>
REDIS_PASSWORD=<使用强密码>
JWT_SECRET_KEY=<生成32位随机字符串>

# 生产环境 CORS
CORS_ORIGINS=https://yourdomain.com

# LLM API密钥
DEEPSEEK_API_KEY=<真实API密钥>

# 前端配置
VITE_API_BASE_URL=https://yourdomain.com
```

**生成安全密钥**:

```bash
# 生成JWT密钥
openssl rand -hex 32

# 生成数据库密码
openssl rand -base64 32
```

### 步骤 2: 构建和启动

```bash
# 使用脚本启动
./scripts/docker-start.sh prod

# 或手动启动
docker-compose -f docker-compose.prod.yml up --build -d
```

### 步骤 3: 配置域名和 SSL

#### 3.1 域名配置

更新 DNS 记录，将域名指向服务器 IP：

```
A    yourdomain.com    -> 123.456.789.0
CNAME www              -> yourdomain.com
```

#### 3.2 配置 SSL/TLS（Let's Encrypt）

安装 Certbot：

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

获取证书：

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

更新 Nginx 配置（`docker/frontend/nginx.conf`）：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    # 其他配置...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

挂载证书到容器（修改 `docker-compose.prod.yml`）：

```yaml
frontend:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### 步骤 4: 生产环境验证

```bash
# 检查服务状态
./scripts/docker-start.sh status

# 查看资源使用
docker stats

# 测试健康检查
curl https://yourdomain.com/health

# 查看日志
./scripts/docker-start.sh logs prod
```

### 生产环境优化

**后端优化**:
- ✅ Gunicorn 多进程 (4 workers)
- ✅ 连接池优化
- ✅ 请求超时配置
- ✅ 日志轮转

**前端优化**:
- ✅ Gzip 压缩
- ✅ 静态资源缓存
- ✅ CDN 集成（可选）
- ✅ 代码分割和懒加载

**数据库优化**:
- ✅ 连接池配置
- ✅ 慢查询日志
- ✅ 定期备份
- ✅ 性能监控

---

## ⚙️ 配置说明

### 环境变量详解

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `DB_NAME` | 数据库名称 | resoftai | 否 |
| `DB_USER` | 数据库用户 | resoftai | 否 |
| `DB_PASSWORD` | 数据库密码 | resoftai123 | **是** |
| `POSTGRES_PORT` | PostgreSQL端口 | 5432 | 否 |
| `REDIS_PASSWORD` | Redis密码 | redis123 | **是** |
| `REDIS_PORT` | Redis端口 | 6379 | 否 |
| `JWT_SECRET_KEY` | JWT密钥 | - | **是** |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间 | 30 | 否 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - | 否* |
| `ANTHROPIC_API_KEY` | Anthropic API密钥 | - | 否* |
| `OPENAI_API_KEY` | OpenAI API密钥 | - | 否* |
| `CORS_ORIGINS` | CORS允许源 | * | 否 |
| `VITE_API_BASE_URL` | 前端API地址 | http://localhost:8000 | 否 |
| `RUN_MIGRATIONS` | 自动运行迁移 | true | 否 |
| `INIT_DB` | 初始化数据库 | true (dev) / false (prod) | 否 |

*注：至少需要配置一个 LLM API 密钥

### Docker Compose 配置

#### 开发环境 (`docker-compose.yml`)

特点：
- 源码热重载
- 详细日志输出
- 开发工具集成
- 快速迭代

#### 生产环境 (`docker-compose.prod.yml`)

特点：
- Gunicorn 多进程
- Nginx 反向代理
- 日志轮转
- 资源限制
- 健康检查
- 自动重启

---

## 📝 常用命令

### 启动脚本命令

```bash
# 启动开发环境
./scripts/docker-start.sh dev

# 启动生产环境
./scripts/docker-start.sh prod

# 停止所有服务
./scripts/docker-start.sh stop

# 重启服务
./scripts/docker-start.sh restart dev
./scripts/docker-start.sh restart prod

# 查看日志
./scripts/docker-start.sh logs dev          # 所有服务日志
./scripts/docker-start.sh logs dev backend  # 指定服务日志
./scripts/docker-start.sh logs prod frontend

# 查看状态
./scripts/docker-start.sh status

# 清理所有容器、卷和镜像
./scripts/docker-start.sh cleanup
```

### Docker Compose 原生命令

```bash
# 构建镜像
docker-compose build
docker-compose build backend  # 只构建backend

# 启动服务
docker-compose up -d
docker-compose up backend  # 只启动backend

# 停止服务
docker-compose stop
docker-compose down  # 停止并删除容器

# 查看日志
docker-compose logs -f
docker-compose logs -f --tail=100 backend

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U resoftai

# 查看资源使用
docker stats

# 清理
docker-compose down -v  # 删除容器和卷
docker system prune -a  # 清理所有未使用的资源
```

### 数据库操作

```bash
# 连接到PostgreSQL
docker-compose exec postgres psql -U resoftai -d resoftai

# 备份数据库
docker-compose exec postgres pg_dump -U resoftai resoftai > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U resoftai -d resoftai < backup.sql

# 运行迁移
docker-compose exec backend alembic upgrade head

# 创建迁移
docker-compose exec backend alembic revision --autogenerate -m "description"
```

---

## 🔧 故障排查

### 常见问题

#### 1. 容器启动失败

**症状**: 容器持续重启或无法启动

**排查步骤**:

```bash
# 查看容器状态
docker-compose ps

# 查看详细日志
docker-compose logs backend

# 检查健康检查
docker inspect resoftai-backend | grep -A 10 Health
```

**可能原因**:
- 数据库未就绪
- 端口被占用
- 环境变量配置错误
- 依赖服务未启动

#### 2. 数据库连接失败

**症状**: Backend 日志显示数据库连接错误

**解决方案**:

```bash
# 检查PostgreSQL状态
docker-compose exec postgres pg_isready -U resoftai

# 检查数据库日志
docker-compose logs postgres

# 验证连接字符串
docker-compose exec backend env | grep DATABASE_URL

# 手动测试连接
docker-compose exec postgres psql -U resoftai -d resoftai -c "SELECT 1;"
```

#### 3. 前端无法访问后端

**症状**: 前端显示 API 连接错误

**检查清单**:

```bash
# 1. 检查后端健康
curl http://localhost:8000/health

# 2. 检查 CORS 配置
docker-compose exec backend env | grep CORS

# 3. 检查网络连接
docker network inspect resoftai-cli_resoftai-network

# 4. 检查 Nginx 配置（生产环境）
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

#### 4. 容器内存不足

**症状**: 容器被 OOM Killer 杀死

**解决方案**:

在 `docker-compose.yml` 中添加资源限制：

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '2.0'
      reservations:
        memory: 1G
        cpus: '1.0'
```

#### 5. 磁盘空间不足

**检查空间使用**:

```bash
# 查看 Docker 磁盘使用
docker system df

# 查看卷使用
docker volume ls
docker volume inspect resoftai-cli_postgres_data

# 清理未使用资源
docker system prune -a --volumes
```

### 日志分析

**查看不同级别的日志**:

```bash
# 错误日志
docker-compose logs backend | grep ERROR

# 最近的日志
docker-compose logs --tail=100 -f backend

# 特定时间范围
docker-compose logs --since 30m backend

# 导出日志到文件
docker-compose logs backend > backend.log
```

---

## 💾 备份和恢复

### 数据库备份

#### 自动备份脚本

创建 `scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/resoftai_$DATE.sql"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump -U resoftai resoftai > "$BACKUP_FILE"

# 压缩备份
gzip "$BACKUP_FILE"

# 保留最近7天的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

#### 定时备份（Cron）

```bash
# 添加到 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/resoftai-cli/scripts/backup-db.sh >> /var/log/resoftai-backup.log 2>&1
```

### 数据恢复

```bash
# 从备份恢复
gunzip < backups/resoftai_20251114_020000.sql.gz | \
    docker-compose exec -T postgres psql -U resoftai -d resoftai

# 或者
docker-compose exec -T postgres psql -U resoftai -d resoftai < backup.sql
```

### 完整系统备份

```bash
#!/bin/bash
# 备份数据库卷
docker run --rm -v resoftai-cli_postgres_data:/data -v $(pwd)/backups:/backup \
    alpine tar czf /backup/postgres_volume_$(date +%Y%m%d).tar.gz -C /data .

# 备份 Redis 数据
docker run --rm -v resoftai-cli_redis_data:/data -v $(pwd)/backups:/backup \
    alpine tar czf /backup/redis_volume_$(date +%Y%m%d).tar.gz -C /data .

# 备份配置文件
tar czf backups/config_$(date +%Y%m%d).tar.gz .env docker-compose*.yml
```

---

## 🎯 最佳实践

### 安全建议

1. **密钥管理**
   - 使用强随机密钥
   - 不要提交 `.env` 到版本控制
   - 定期轮换密钥

2. **网络安全**
   - 使用 HTTPS
   - 配置防火墙规则
   - 限制数据库访问

3. **容器安全**
   - 使用非 root 用户运行
   - 最小化镜像体积
   - 定期更新基础镜像

### 性能优化

1. **资源限制**
   - 合理配置内存和 CPU 限制
   - 使用健康检查
   - 配置重启策略

2. **缓存策略**
   - 使用 Redis 缓存
   - 配置 HTTP 缓存头
   - 使用 CDN

3. **监控和告警**
   - 配置健康检查
   - 集成日志收集
   - 设置性能监控

---

## 📞 技术支持

如遇到问题，请通过以下方式获取帮助：

1. **查看文档**: [完整文档](../README.md)
2. **提交Issue**: [GitHub Issues](https://github.com/softctwo/resoftai-cli/issues)
3. **邮件联系**: softctwo@aliyun.com

---

**文档版本**: 1.0
**最后更新**: 2025-11-14
**维护者**: Claude
