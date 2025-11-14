# Load Testing

性能和负载测试工具，用于测试ResoftAI平台的WebSocket协作编辑功能。

## 工具

### 1. Locust (HTTP + WebSocket)

Locust是一个开源的负载测试工具，支持HTTP和WebSocket测试。

#### 安装

```bash
pip install locust python-socketio[client]
```

#### 运行

```bash
# 启动Locust Web界面
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 或使用命令行模式
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 --run-time 60s --headless
```

#### 参数说明

- `--host`: 目标服务器URL
- `--users`: 模拟用户数量
- `--spawn-rate`: 每秒启动的用户数
- `--run-time`: 测试持续时间
- `--headless`: 无头模式（命令行）

#### Web界面

访问 http://localhost:8089 打开Locust Web界面：

1. 设置用户数量（Number of users）
2. 设置启动速率（Spawn rate）
3. 点击 "Start swarming" 开始测试
4. 查看实时统计和图表

### 2. 简单WebSocket负载测试

纯Python异步WebSocket负载测试脚本。

#### 安装

```bash
pip install python-socketio[asyncio_client]
```

#### 运行

```bash
# 基本用法
python tests/load/websocket_load_test.py

# 自定义参数
python tests/load/websocket_load_test.py \
    --url ws://localhost:8000 \
    --users 50 \
    --duration 60
```

#### 参数说明

- `--url`: WebSocket服务器URL（默认：ws://localhost:8000）
- `--users`: 并发用户数（默认：10）
- `--duration`: 测试时长（秒，默认：30）

#### 输出示例

```
============================================================
WebSocket Load Test
============================================================
Server: ws://localhost:8000
Users: 50
Duration: 60s
============================================================

Test Results
============================================================
Elapsed time: 60.23s
Total messages sent: 2450
Total messages received: 9800
Total errors: 0
Messages per second: 40.68

Latency Statistics:
  Average: 12.34ms
  Median: 10.21ms
  Min: 3.45ms
  Max: 89.12ms
  P95: 25.67ms
  P99: 45.23ms
============================================================
```

## 测试场景

### 场景1: 基础负载测试

测试系统在正常负载下的性能。

```bash
# 10个用户，持续30秒
python tests/load/websocket_load_test.py --users 10 --duration 30
```

### 场景2: 中等负载测试

模拟中等规模的协作编辑场景。

```bash
# 50个用户，持续60秒
python tests/load/websocket_load_test.py --users 50 --duration 60
```

### 场景3: 高负载测试

测试系统的极限承载能力。

```bash
# 100个用户，持续120秒
python tests/load/websocket_load_test.py --users 100 --duration 120
```

### 场景4: 压力测试

逐步增加负载直到系统出现问题。

```bash
# 使用Locust逐步增加用户
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
    --users 200 --spawn-rate 5 --run-time 300s --headless
```

## 性能指标

### 关键指标

1. **响应时间**
   - 平均响应时间（Average Response Time）
   - P95响应时间（95th Percentile）
   - P99响应时间（99th Percentile）

2. **吞吐量**
   - 每秒请求数（RPS - Requests Per Second）
   - 每秒消息数（MPS - Messages Per Second）

3. **错误率**
   - 失败请求百分比
   - WebSocket连接错误
   - 消息发送失败

4. **并发性**
   - 同时在线用户数
   - 活跃连接数

### 性能目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 平均响应时间 | < 100ms | WebSocket消息往返时间 |
| P95响应时间 | < 200ms | 95%的请求应在此时间内完成 |
| P99响应时间 | < 500ms | 99%的请求应在此时间内完成 |
| 错误率 | < 1% | 失败请求占比 |
| 并发用户 | ≥ 100 | 系统应支持至少100个并发用户 |
| 消息吞吐量 | ≥ 1000 MPS | 每秒处理至少1000条消息 |

## 监控

### 实时监控

在负载测试期间，使用性能监控API获取实时指标：

```bash
# 获取性能指标
curl http://localhost:8000/api/performance/metrics

# 获取WebSocket指标
curl http://localhost:8000/api/performance/websocket

# 获取特定操作的耗时统计
curl http://localhost:8000/api/performance/timing/manager.broadcast_to_file
```

### 系统资源监控

使用系统工具监控服务器资源使用：

```bash
# CPU和内存使用
top -p $(pgrep -f uvicorn)

# 网络连接
netstat -ant | grep :8000 | wc -l

# 查看进程详情
ps aux | grep uvicorn
```

## 结果分析

### 成功标准

测试被认为成功如果：

1. ✅ 错误率 < 1%
2. ✅ 平均响应时间 < 100ms
3. ✅ P95响应时间 < 200ms
4. ✅ 系统保持稳定（无崩溃、无内存泄漏）
5. ✅ 所有用户能成功连接和断开

### 失败分析

如果测试失败，检查：

1. **高错误率**
   - 检查服务器日志
   - 查看WebSocket连接限制
   - 检查数据库连接池

2. **高延迟**
   - 检查网络带宽
   - 查看CPU使用率
   - 分析数据库查询性能

3. **连接失败**
   - 检查最大连接数限制
   - 查看文件描述符限制（ulimit）
   - 检查防火墙设置

## 优化建议

### 服务器优化

1. **增加工作进程数**
   ```bash
   uvicorn main:app --workers 4
   ```

2. **启用Redis缓存**
   ```bash
   export REDIS_URL=redis://localhost:6379/0
   ```

3. **数据库连接池**
   ```python
   # 增加连接池大小
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=10
   )
   ```

### 应用优化

1. **消息批处理**
   - 合并小消息减少网络往返
   - 使用MessageBatcher工具

2. **缓存策略**
   - 缓存文件内容
   - 缓存用户信息
   - 使用Redis存储会话状态

3. **数据库优化**
   - 添加索引
   - 优化查询
   - 使用连接池

## 故障排除

### 常见问题

**Q: WebSocket连接失败**
```bash
# 检查服务器是否运行
curl http://localhost:8000/health

# 检查WebSocket端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/socket.io/
```

**Q: 测试脚本报错**
```bash
# 安装缺失依赖
pip install -r requirements-test.txt

# 检查Python版本（需要3.8+）
python --version
```

**Q: 性能指标不准确**
```bash
# 重置性能监控
curl -X POST http://localhost:8000/api/performance/reset

# 重新运行测试
python tests/load/websocket_load_test.py
```

## 最佳实践

1. **预热系统**
   - 在正式测试前运行小规模预热测试
   - 确保所有服务已启动

2. **逐步增加负载**
   - 从小规模开始（10用户）
   - 逐步增加到目标负载
   - 观察系统响应

3. **多次测试**
   - 运行多次获取平均值
   - 消除偶然因素影响

4. **记录结果**
   - 保存测试报告
   - 记录系统配置
   - 对比不同版本

5. **真实场景模拟**
   - 模拟实际用户行为
   - 使用真实数据量
   - 考虑网络延迟

## 参考资料

- [Locust文档](https://docs.locust.io/)
- [Python-SocketIO客户端](https://python-socketio.readthedocs.io/)
- [性能测试最佳实践](https://www.softwaretestinghelp.com/performance-testing-best-practices/)
