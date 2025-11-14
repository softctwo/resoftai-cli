# 性能优化指南

ResoftAI平台的性能优化和负载测试完整指南。

## 目录

- [概述](#概述)
- [性能监控](#性能监控)
- [缓存策略](#缓存策略)
- [数据库优化](#数据库优化)
- [WebSocket优化](#websocket优化)
- [负载测试](#负载测试)
- [部署优化](#部署优化)
- [故障排查](#故障排查)

## 概述

本文档描述了ResoftAI平台实施的性能优化措施，包括：

- ✅ 性能监控和指标收集
- ✅ Redis缓存集成
- ✅ 数据库查询优化
- ✅ WebSocket消息批处理
- ✅ 负载测试工具
- ✅ 性能分析API

## 性能监控

### PerformanceMonitor

自动收集和分析性能指标。

#### 使用方法

```python
from resoftai.utils.performance import performance_monitor, timing_decorator

# 使用装饰器自动记录函数执行时间
@timing_decorator("my_operation")
async def my_function():
    # Your code here
    pass

# 手动记录指标
performance_monitor.record_timing("custom_metric", duration_seconds)
performance_monitor.increment_counter("api_calls")

# 获取统计数据
stats = performance_monitor.get_stats("my_operation")
# Returns: {'min': 0.1, 'max': 2.5, 'avg': 0.8, 'count': 100, 'total': 80.0}
```

### WebSocket监控

专门用于WebSocket连接和消息的指标。

```python
from resoftai.utils.performance import websocket_metrics

# 自动在ConnectionManager中调用
websocket_metrics.connection_opened()
websocket_metrics.message_sent(size_bytes)
websocket_metrics.message_received(size_bytes)

# 获取统计
stats = websocket_metrics.get_stats()
# Returns:
# {
#     'active_connections': 45,
#     'total_connections': 523,
#     'messages_sent': 12456,
#     'bytes_sent': 3456789,
#     'avg_message_size_sent': 277.5,
#     ...
# }
```

### 性能报告API

通过HTTP API访问性能指标：

```bash
# 获取综合性能报告
curl http://localhost:8000/api/performance/metrics

# 获取WebSocket指标
curl http://localhost:8000/api/performance/websocket

# 获取特定操作的耗时统计
curl http://localhost:8000/api/performance/timing/crud.get_project_by_id

# 重置指标（需要认证）
curl -X POST http://localhost:8000/api/performance/reset \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 监控示例输出

```json
{
  "timestamp": "2025-11-14T10:30:45.123Z",
  "performance_metrics": {
    "manager.connect": {
      "min": 0.005,
      "max": 0.124,
      "avg": 0.023,
      "count": 523,
      "total": 12.029
    },
    "manager.broadcast_to_file": {
      "min": 0.002,
      "max": 0.089,
      "avg": 0.015,
      "count": 12456,
      "total": 186.84
    }
  },
  "websocket_metrics": {
    "active_connections": 45,
    "total_connections": 523,
    "messages_sent": 12456,
    "bytes_sent": 3456789
  }
}
```

## 缓存策略

### Redis缓存

使用Redis缓存频繁访问的数据以减少数据库负载。

#### 配置

```bash
# 环境变量
export REDIS_URL=redis://localhost:6379/0

# 或在.env文件中
REDIS_URL=redis://localhost:6379/0
```

#### 使用缓存装饰器

```python
from resoftai.utils.cache import cached, cache_manager

# 缓存函数结果
@cached(key_func=lambda user_id: f"user:{user_id}", ttl=300)
async def get_user(user_id: int):
    # Expensive database query
    return user_data

# 手动缓存操作
await cache_manager.set("my_key", {"data": "value"}, ttl=600)
value = await cache_manager.get("my_key")
await cache_manager.delete("my_key")

# 清除模式匹配的键
deleted_count = await cache_manager.clear_pattern("user:*")
```

#### 缓存失效策略

```python
# CRUD操作中自动失效缓存
async def update_project(db, project_id, **kwargs):
    project = await _update_project_in_db(db, project_id, **kwargs)

    # 失效缓存
    await cache_manager.delete(f"project:{project_id}")
    await cache_manager.clear_pattern(f"user:{project.user_id}:projects:*")

    return project
```

### 速率限制

使用Redis实现API速率限制。

```python
from resoftai.utils.cache import rate_limiter

# 检查是否允许请求
is_allowed = await rate_limiter.is_allowed(
    key=f"user:{user_id}",
    max_requests=100,  # 最大请求数
    window_seconds=60  # 时间窗口（秒）
)

if not is_allowed:
    raise HTTPException(status_code=429, detail="Too many requests")
```

### 缓存最佳实践

1. **选择合适的TTL**
   - 用户数据：5-15分钟
   - 项目列表：3-5分钟
   - 配置数据：30-60分钟
   - 静态内容：1-24小时

2. **缓存键命名规范**
   ```
   {prefix}:{entity}:{id}:{sub_key}
   例如:
   resoftai:project:123
   resoftai:user:456:projects:active
   ```

3. **缓存失效策略**
   - 写操作后立即失效相关缓存
   - 使用模式匹配批量清除
   - 设置合理的TTL作为后备

## 数据库优化

### 索引优化

添加的性能索引：

```sql
-- Projects表
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_user_status ON projects(user_id, status);

-- Files表
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_files_path ON files(path);

-- Agent Activities表
CREATE INDEX idx_agent_activities_project_id ON agent_activities(project_id);
CREATE INDEX idx_agent_activities_project_created ON agent_activities(project_id, created_at);

-- Users表
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

#### 运行迁移

```bash
# 应用性能索引
alembic upgrade head

# 回滚（如果需要）
alembic downgrade -1
```

### 查询优化

#### 批量操作

使用批量操作代替多次单个查询：

```python
# ❌ 不好: N+1 查询
for project_id in project_ids:
    project = await get_project_by_id(db, project_id)
    # Process project...

# ✅ 好: 批量查询
projects = await get_projects_by_ids(db, project_ids)
for project in projects:
    # Process project...
```

#### 批量更新

```python
# ❌ 不好: 多次单个更新
for project_id in project_ids:
    await update_project(db, project_id, status="completed")

# ✅ 好: 批量更新
count = await bulk_update_project_status(db, project_ids, "completed")
```

#### 预加载关联数据

```python
from sqlalchemy.orm import selectinload

# 预加载关联数据避免N+1查询
query = select(Project).options(
    selectinload(Project.files),
    selectinload(Project.agent_activities)
).where(Project.id == project_id)
```

### 连接池配置

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # 连接池大小
    max_overflow=10,       # 最大溢出连接数
    pool_timeout=30,       # 获取连接超时
    pool_recycle=3600,     # 连接回收时间
    pool_pre_ping=True,    # 连接健康检查
    echo=False             # 生产环境禁用SQL日志
)
```

### 查询性能分析

```python
# 启用查询日志（开发环境）
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 分析慢查询
from sqlalchemy import event

@event.listens_for(engine.sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(engine.sync_engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # 记录超过100ms的查询
        logger.warning(f"Slow query ({total:.3f}s): {statement}")
```

## WebSocket优化

### 消息批处理

使用MessageBatcher合并小消息：

```python
from resoftai.utils.performance import message_batcher

async def flush_messages(messages):
    # 批量发送消息
    await sio.emit('batch_update', {'messages': messages})

# 添加消息到批处理队列
await message_batcher.add_message(
    key=f"file:{file_id}",
    message=cursor_data,
    flush_callback=flush_messages
)
```

配置参数：
- `batch_size`: 每批最大消息数（默认：10）
- `flush_interval`: 刷新间隔（默认：0.1秒）

### 连接管理

```python
# Socket.IO服务器配置
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    max_http_buffer_size=1024 * 1024,  # 1MB
    ping_timeout=60,                    # Ping超时
    ping_interval=25,                   # Ping间隔
    compression_threshold=1024,         # 压缩阈值
)
```

### 防抖优化

客户端防抖减少消息频率：

```javascript
// 编辑防抖 (300ms)
const debouncedSendEdit = debounce((changes) => {
  socket.emit('file_edit', { file_id, changes })
}, 300)

// 光标防抖 (500ms)
const debouncedSendCursor = debounce((position) => {
  socket.emit('cursor_position', { file_id, position })
}, 500)
```

## 负载测试

详细的负载测试文档见 [tests/load/README.md](../tests/load/README.md)

### 快速开始

```bash
# 安装依赖
pip install locust python-socketio[asyncio_client]

# WebSocket负载测试
python tests/load/websocket_load_test.py \
  --url ws://localhost:8000 \
  --users 50 \
  --duration 60

# Locust负载测试（Web界面）
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

### 性能目标

| 指标 | 目标值 |
|------|--------|
| 平均响应时间 | < 100ms |
| P95响应时间 | < 200ms |
| P99响应时间 | < 500ms |
| 错误率 | < 1% |
| 并发用户 | ≥ 100 |
| 消息吞吐量 | ≥ 1000 MPS |

## 部署优化

### 生产环境配置

```bash
# 使用多个工作进程
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --log-level info

# 使用Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --keep-alive 5 \
  --max-requests 1000 \
  --max-requests-jitter 50
```

### Nginx反向代理

```nginx
upstream resoftai_backend {
    least_conn;  # 最少连接负载均衡
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name api.resoftai.com;

    # WebSocket支持
    location /socket.io/ {
        proxy_pass http://resoftai_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # HTTP API
    location / {
        proxy_pass http://resoftai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 缓存静态资源
        proxy_cache_valid 200 10m;
        proxy_cache_bypass $http_pragma $http_authorization;
    }

    # 连接限制
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    limit_conn addr 20;

    # 请求速率限制
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

### Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install uvloop

# 复制代码
COPY . .

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --loop uvloop \
    --no-access-log
```

### 系统优化

```bash
# 增加文件描述符限制
ulimit -n 65535

# /etc/security/limits.conf
* soft nofile 65535
* hard nofile 65535

# 优化TCP设置
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_tw_reuse = 1
```

## 故障排查

### 性能问题诊断

#### 1. 高延迟

检查清单：
- [ ] 查看性能监控API找出慢操作
- [ ] 启用SQL日志查找慢查询
- [ ] 检查Redis连接状态
- [ ] 查看CPU和内存使用率
- [ ] 分析网络延迟

```bash
# 获取性能指标
curl http://localhost:8000/api/performance/metrics | jq '.performance_metrics'

# 检查慢查询（查看日志）
grep "Slow query" /var/log/resoftai/app.log

# 系统资源
top -p $(pgrep -f uvicorn)
```

#### 2. 高错误率

```bash
# 查看WebSocket错误
curl http://localhost:8000/api/performance/websocket | jq '.errors'

# 检查应用日志
tail -f /var/log/resoftai/app.log | grep ERROR

# 数据库连接
psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='resoftai';"
```

#### 3. 内存泄漏

```bash
# 监控内存使用
ps aux | grep uvicorn | awk '{print $6}'

# Python内存分析
pip install memory_profiler
python -m memory_profiler your_script.py
```

### 常见问题

**Q: Redis连接失败**
```bash
# 检查Redis状态
redis-cli ping

# 检查连接配置
echo $REDIS_URL

# 测试连接
redis-cli -u $REDIS_URL ping
```

**Q: 数据库连接池耗尽**
```python
# 增加连接池大小
engine = create_async_engine(
    DATABASE_URL,
    pool_size=30,  # 增加到30
    max_overflow=20  # 增加溢出数
)
```

**Q: WebSocket连接频繁断开**
```python
# 调整超时设置
sio = socketio.AsyncServer(
    ping_timeout=120,  # 增加到120秒
    ping_interval=25
)
```

## 性能优化检查清单

部署前确保：

- [ ] 启用Redis缓存
- [ ] 运行数据库索引迁移
- [ ] 配置连接池大小
- [ ] 设置合理的缓存TTL
- [ ] 启用性能监控
- [ ] 运行负载测试
- [ ] 配置Nginx反向代理
- [ ] 设置系统资源限制
- [ ] 启用日志记录
- [ ] 配置健康检查

## 监控仪表板

建议使用以下工具建立监控仪表板：

1. **Grafana** - 可视化性能指标
2. **Prometheus** - 指标收集
3. **ELK Stack** - 日志分析
4. **New Relic / DataDog** - APM监控

示例Grafana查询：

```promql
# 平均响应时间
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# WebSocket活跃连接
websocket_active_connections

# 缓存命中率
rate(cache_hits[5m]) / (rate(cache_hits[5m]) + rate(cache_misses[5m]))
```

## 参考资料

- [FastAPI性能优化](https://fastapi.tiangolo.com/deployment/server-workers/)
- [SQLAlchemy性能指南](https://docs.sqlalchemy.org/en/14/faq/performance.html)
- [Redis最佳实践](https://redis.io/topics/optimization)
- [WebSocket优化](https://socket.io/docs/v4/performance-tuning/)

---

**版本**: 1.0.0
**最后更新**: 2025-11-14
**作者**: ResoftAI Team
