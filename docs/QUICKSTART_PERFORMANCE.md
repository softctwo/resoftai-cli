# 性能优化快速启动指南

快速配置和使用ResoftAI性能优化功能。

## 🚀 5分钟快速启动

### 1. 运行自动配置脚本

```bash
# 自动安装和配置所有性能优化组件
./scripts/setup_performance.sh
```

这个脚本会自动：
- ✅ 检查Python版本
- ✅ 安装和启动Redis
- ✅ 安装性能监控依赖
- ✅ 安装负载测试工具
- ✅ 运行数据库迁移添加性能索引
- ✅ 创建和配置.env文件
- ✅ 测试Redis连接
- ✅ 创建日志目录

### 2. 手动配置（可选）

如果您不想使用自动脚本：

```bash
# 1. 安装Redis
sudo apt-get install redis-server
sudo systemctl start redis

# 2. 安装Python依赖
pip install redis locust python-socketio[asyncio_client]

# 3. 复制并配置环境文件
cp .env.example .env
# 编辑.env，确保REDIS_URL正确配置

# 4. 运行数据库迁移
alembic upgrade head
```

### 3. 启动服务

```bash
# 使用多个工作进程启动（推荐生产环境）
uvicorn src.resoftai.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用开发模式（自动重载）
uvicorn src.resoftai.api.main:app --reload
```

### 4. 验证性能功能

```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看性能指标
curl http://localhost:8000/api/performance/metrics | jq

# 查看WebSocket指标
curl http://localhost:8000/api/performance/websocket | jq
```

## 📊 性能监控

### 实时监控

```bash
# 持续监控性能指标（每5秒刷新）
watch -n 5 'curl -s http://localhost:8000/api/performance/metrics | jq'

# 只查看WebSocket统计
watch -n 2 'curl -s http://localhost:8000/api/performance/websocket | jq'
```

### 查看特定操作耗时

```bash
# WebSocket连接耗时
curl http://localhost:8000/api/performance/timing/manager.connect | jq

# 文件广播耗时
curl http://localhost:8000/api/performance/timing/manager.broadcast_to_file | jq

# 数据库查询耗时
curl http://localhost:8000/api/performance/timing/crud.get_project_by_id | jq
```

## 🧪 负载测试

### WebSocket负载测试

```bash
# 基础测试 - 10个用户，30秒
python tests/load/websocket_load_test.py --users 10 --duration 30

# 中等负载 - 50个用户，60秒
python tests/load/websocket_load_test.py \
  --url ws://localhost:8000 \
  --users 50 \
  --duration 60

# 压力测试 - 100个用户，120秒
python tests/load/websocket_load_test.py --users 100 --duration 120
```

### Locust Web界面测试

```bash
# 启动Locust Web界面
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 访问 http://localhost:8089
# 配置用户数和启动速率，然后开始测试
```

### Locust命令行测试

```bash
# 无头模式运行
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 60s \
  --headless \
  --csv=results
```

## 💾 Redis缓存

### 验证缓存工作

```bash
# 检查Redis连接
redis-cli ping
# 应该返回: PONG

# 查看缓存的键
redis-cli KEYS "resoftai:*"

# 查看特定缓存
redis-cli GET "resoftai:project:1"

# 清空所有缓存
redis-cli FLUSHDB
```

### 监控缓存命中率

```python
# 在代码中添加缓存监控
from resoftai.utils.cache import cache_manager

# 查看缓存键
keys = await cache_manager.scan_iter("resoftai:*")

# 手动清理过期缓存
await cache_manager.clear_pattern("user:*")
```

## 🗄️ 数据库优化

### 验证索引已创建

```sql
-- 连接到数据库
psql -d resoftai

-- 查看所有索引
\di

-- 查看projects表的索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'projects';

-- 分析查询计划
EXPLAIN ANALYZE SELECT * FROM projects WHERE user_id = 1 ORDER BY created_at DESC;
```

### 监控慢查询

查看应用日志中的慢查询警告：

```bash
# 查看最近的慢查询
tail -f /var/log/resoftai/app.log | grep "Slow query"

# 或使用jq格式化JSON日志
tail -f /var/log/resoftai/app.log | jq 'select(.message | contains("Slow query"))'
```

## 📈 性能基准

### 期望的性能指标

在标准硬件上（4核CPU，8GB RAM），您应该看到：

| 指标 | 期望值 |
|------|--------|
| API平均响应时间 | < 50ms |
| WebSocket消息延迟 | < 20ms |
| 数据库查询时间 | < 30ms |
| 缓存命中响应时间 | < 5ms |
| 并发WebSocket连接 | > 100 |
| 每秒请求数 | > 500 |

### 运行基准测试

```bash
# 1. 运行短期负载测试
python tests/load/websocket_load_test.py --users 50 --duration 30

# 2. 查看性能报告
curl http://localhost:8000/api/performance/metrics | jq

# 3. 记录关键指标
curl http://localhost:8000/api/performance/metrics | \
  jq '.performance_metrics | to_entries[] | {name: .key, avg: .value.avg}'
```

## 🔧 故障排查

### Redis连接问题

```bash
# 检查Redis是否运行
systemctl status redis

# 重启Redis
sudo systemctl restart redis

# 检查Redis日志
sudo tail -f /var/log/redis/redis-server.log

# 测试连接
redis-cli -h localhost -p 6379 ping
```

### 性能问题诊断

```bash
# 1. 检查系统资源
top -p $(pgrep -f uvicorn)

# 2. 查看数据库连接
psql -d resoftai -c "SELECT count(*) FROM pg_stat_activity;"

# 3. 查看WebSocket连接
curl http://localhost:8000/api/performance/websocket | jq '.active_connections'

# 4. 重置性能指标
curl -X POST http://localhost:8000/api/performance/reset
```

### 高延迟问题

如果出现高延迟：

1. **检查慢查询**
   ```bash
   tail -f /var/log/resoftai/app.log | grep "Slow query"
   ```

2. **查看数据库索引使用情况**
   ```sql
   SELECT schemaname, tablename, indexname, idx_scan
   FROM pg_stat_user_indexes
   ORDER BY idx_scan ASC;
   ```

3. **增加数据库连接池**
   编辑.env：
   ```
   DB_POOL_SIZE=30
   DB_MAX_OVERFLOW=20
   ```

4. **检查Redis性能**
   ```bash
   redis-cli --latency
   redis-cli --stat
   ```

## 📚 进一步学习

- **完整性能优化指南**: [PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md)
- **负载测试文档**: [tests/load/README.md](../tests/load/README.md)
- **协作编辑文档**: [COLLABORATIVE_EDITING.md](./COLLABORATIVE_EDITING.md)

## 🎯 生产环境部署

### 推荐配置

```bash
# .env生产配置
REDIS_URL=redis://localhost:6379/0
DB_POOL_SIZE=30
DB_MAX_OVERFLOW=20
API_WORKERS=8
ENABLE_CACHE=true
DEFAULT_CACHE_TTL=600
LOG_LEVEL=WARNING
```

### 使用Nginx反向代理

```nginx
upstream resoftai_backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.resoftai.com;

    location /socket.io/ {
        proxy_pass http://resoftai_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://resoftai_backend;
    }
}
```

### Docker Compose部署

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres@db/resoftai
    depends_on:
      - redis
      - db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=resoftai
```

## ✅ 检查清单

部署前确认：

- [ ] Redis已安装并运行
- [ ] 数据库迁移已执行
- [ ] .env文件已正确配置
- [ ] 性能监控API可访问
- [ ] 负载测试通过
- [ ] 缓存正常工作
- [ ] 日志目录已创建
- [ ] 系统资源限制已调整（ulimit）
- [ ] Nginx/反向代理已配置
- [ ] 监控告警已设置

## 🆘 获取帮助

- 查看日志: `tail -f /var/log/resoftai/app.log`
- 性能问题: 查看 [PERFORMANCE_OPTIMIZATION.md](./PERFORMANCE_OPTIMIZATION.md)
- 负载测试: 查看 [tests/load/README.md](../tests/load/README.md)
- 提交Issue: [GitHub Issues](https://github.com/softctwo/resoftai-cli/issues)

---

**提示**: 性能优化是一个持续的过程。定期运行负载测试和监控指标，根据实际使用情况调整配置。
