# ResoftAI Performance Testing Suite

完整的性能测试工具集，用于评估 ResoftAI API 和 WebSocket 的性能表现。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [测试工具](#测试工具)
3. [测试场景](#测试场景)
4. [性能指标](#性能指标)
5. [运行测试](#运行测试)
6. [报告分析](#报告分析)
7. [故障排查](#故障排查)

---

## 🚀 快速开始

### 安装依赖

```bash
# 安装性能测试依赖
pip install -r tests/performance/requirements.txt
```

### 启动后端服务

```bash
# 确保后端服务已启动
./scripts/docker-start.sh dev
# 或
PYTHONPATH=src uvicorn resoftai.api.main:asgi_app --reload
```

### 运行快速smoke测试

```bash
# 运行1分钟smoke测试
./tests/performance/run_performance_tests.sh smoke
```

---

## 🛠️ 测试工具

### 1. Locust API负载测试

**文件**: `locustfile.py`

基于 Locust 的 HTTP API 性能测试，支持：
- ✅ 多用户并发测试
- ✅ 真实用户行为模拟
- ✅ 自动化注册和登录
- ✅ 覆盖所有主要 API 端点
- ✅ 详细的性能报告

**测试的 API 端点**:
- 健康检查 (`/health`)
- 用户认证 (`/api/auth/*`)
- 项目管理 (`/api/projects/*`)
- 文件管理 (`/api/files/*`)
- LLM 配置 (`/api/llm-configs/*`)
- 代理活动 (`/api/agent-activities/*`)
- 代码质量检查 (`/api/code-quality/*`)
- 模板管理 (`/api/v1/templates/*`)

### 2. WebSocket压力测试

**文件**: `websocket_test.py`

基于 Socket.IO 的 WebSocket 性能测试，支持：
- ✅ 并发连接测试 (1-1000+ connections)
- ✅ 消息延迟测量
- ✅ 连接稳定性测试
- ✅ 自动重连测试
- ✅ 错误率统计

**测试指标**:
- 连接时间
- 消息往返延迟 (RTT)
- 消息传递率
- 错误率

### 3. 性能配置

**文件**: `performance_config.py`

定义性能测试的配置和阈值：
- 性能基准线
- 测试场景参数
- 负载模式
- 报告配置

---

## 📊 测试场景

### 1. Smoke Test (冒烟测试)

**目的**: 快速验证系统基本功能

**配置**:
- 用户数: 1
- 持续时间: 1分钟
- 用途: CI/CD 集成

**运行**:
```bash
./tests/performance/run_performance_tests.sh smoke
```

### 2. Baseline Test (基准测试)

**目的**: 建立性能基准线

**配置**:
- 用户数: 10
- 生成速率: 2 users/sec
- 持续时间: 5分钟

**运行**:
```bash
./tests/performance/run_performance_tests.sh baseline
```

### 3. Stress Test (压力测试)

**目的**: 测试系统在高负载下的表现

**配置**:
- 用户数: 100
- 生成速率: 10 users/sec
- 持续时间: 15分钟

**运行**:
```bash
./tests/performance/run_performance_tests.sh stress
```

### 4. Spike Test (峰值测试)

**目的**: 测试系统应对突发流量的能力

**配置**:
- 用户数: 0 → 200
- 生成速率: 50 users/sec
- 持续时间: 5分钟

**运行**:
```bash
./tests/performance/run_performance_tests.sh spike
```

### 5. Endurance Test (耐久测试)

**目的**: 测试系统长时间运行的稳定性

**配置**:
- 用户数: 50
- 持续时间: 60分钟

**运行**:
```bash
./tests/performance/run_performance_tests.sh endurance
```

### 6. WebSocket Test

**目的**: 测试 WebSocket 连接性能

**配置**:
- 并发连接: 100-1000
- 持续时间: 60秒

**运行**:
```bash
./tests/performance/run_performance_tests.sh websocket 100 60
```

### 7. Custom Test (自定义测试)

**目的**: 根据特定需求自定义测试参数

**运行**:
```bash
# 格式: custom <users> <spawn_rate> <duration>
./tests/performance/run_performance_tests.sh custom 50 5 10m
```

---

## 📈 性能指标

### API 性能指标

#### 响应时间 (Response Time)

- **P50 (中位数)**: < 100ms ✅ 优秀
- **P95**: < 500ms ✅ 良好
- **P99**: < 1000ms ⚠️ 可接受

#### 吞吐量 (Throughput)

- **目标**: > 100 requests/sec
- **测量**: 总请求数 / 测试时长

#### 错误率 (Error Rate)

- **目标**: < 1% ✅
- **可接受**: < 5% ⚠️
- **不可接受**: > 5% ❌

#### 并发用户

- **轻负载**: 1-10 users
- **正常负载**: 10-50 users
- **高负载**: 50-100 users
- **压力测试**: 100-500 users

### WebSocket 性能指标

#### 连接性能

- **连接时间**: < 1000ms
- **并发连接**: 支持 100+ 连接

#### 消息延迟

- **平均延迟**: < 50ms ✅ 优秀
- **P95延迟**: < 100ms ✅ 良好
- **P99延迟**: < 200ms ⚠️ 可接受

#### 稳定性

- **消息传递率**: > 99%
- **错误率**: < 1%

---

## 🏃 运行测试

### 使用测试脚本

```bash
# 查看帮助
./tests/performance/run_performance_tests.sh help

# 运行单个测试
./tests/performance/run_performance_tests.sh baseline

# 运行所有测试
./tests/performance/run_performance_tests.sh all

# 指定后端地址
API_HOST=http://production.example.com ./tests/performance/run_performance_tests.sh stress
```

### 使用 Locust 命令行

```bash
# 无头模式（自动运行）
locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users=50 \
    --spawn-rate=5 \
    --run-time=5m \
    --headless \
    --html=report.html

# 交互模式（Web UI）
locust -f tests/performance/locustfile.py --host=http://localhost:8000
# 访问 http://localhost:8089
```

### 使用 Python 直接运行

```bash
# WebSocket测试
python tests/performance/websocket_test.py \
    --url http://localhost:8000 \
    --connections 100 \
    --duration 60
```

---

## 📊 报告分析

### HTML 报告

测试完成后，会在 `tests/performance/reports/` 目录生成 HTML 报告：

```bash
# 查看报告
open tests/performance/reports/baseline_test_20251114_100000.html
```

**报告内容**:
- 📊 总体统计
- 📈 响应时间分布
- 📉 每秒请求数 (RPS) 趋势
- ❌ 失败请求详情
- 📋 各端点性能对比

### CSV 报告

CSV 报告包含详细的原始数据，可用于进一步分析：

```bash
# 查看CSV报告
cat tests/performance/reports/baseline_test_20251114_100000_stats.csv
```

**CSV 文件**:
- `*_stats.csv` - 请求统计
- `*_stats_history.csv` - 时间序列数据
- `*_failures.csv` - 失败记录

### 分析性能瓶颈

#### 1. 识别慢端点

查看 HTML 报告中的 "Statistics" 表格，按平均响应时间排序：

```
Endpoint                      | Requests | Avg (ms) | P95 (ms) | P99 (ms)
------------------------------|----------|----------|----------|----------
/api/code-quality/check       | 1000     | 850      | 1200     | 1500
/api/projects/{id}            | 5000     | 45       | 120      | 200
```

**解读**: `/api/code-quality/check` 明显较慢，需要优化。

#### 2. 分析错误模式

查看 "Failures" 表格：

```
Method | Name              | Error                | Occurrences
-------|-------------------|----------------------|------------
POST   | /api/projects     | Connection timeout   | 15
GET    | /api/files        | 500 Internal Error   | 8
```

**解读**: 需要调查 connection timeout 和 500 错误的原因。

#### 3. 评估吞吐量

查看 "Charts" 中的 RPS (Requests Per Second) 图表：

- **稳定**: RPS 保持恒定 ✅
- **下降**: 随时间下降 ❌ (可能有内存泄漏)
- **波动**: 大幅波动 ⚠️ (可能资源竞争)

#### 4. WebSocket 性能分析

运行 WebSocket 测试后，查看输出：

```
📊 WebSocket Performance Test Results
====================================
🔌 Connection Performance:
   - Mean connection time: 125.50ms
   - P95 connection time: 250.00ms

📨 Message Latency:
   - Mean latency: 35.20ms
   - P95 latency: 75.00ms
   - P99 latency: 120.00ms

🎯 Performance Assessment:
   ✅ EXCELLENT - Average latency < 50ms
```

---

## 🔧 故障排查

### 问题 1: Locust 安装失败

**错误**:
```
ERROR: Could not find a version that satisfies the requirement locust
```

**解决**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用特定版本
pip install locust==2.20.0
```

### 问题 2: 后端连接失败

**错误**:
```
[ERROR] Backend is not accessible at http://localhost:8000
```

**解决**:
1. 确认后端已启动
2. 检查端口是否正确
3. 验证健康检查端点：`curl http://localhost:8000/health`

### 问题 3: 认证失败率高

**症状**: 大量 401 Unauthorized 错误

**可能原因**:
- Token 过期时间太短
- 并发注册冲突
- JWT 配置问题

**解决**:
- 增加 token 过期时间
- 调整用户生成逻辑
- 检查 JWT 配置

### 问题 4: WebSocket 连接不稳定

**症状**: 连接频繁断开

**解决**:
```bash
# 检查 WebSocket 配置
# 增加超时时间
# 确认网络稳定性
```

### 问题 5: 内存不足

**症状**: 测试过程中系统变慢或崩溃

**解决**:
- 减少并发用户数
- 增加系统内存
- 分批运行测试
- 监控系统资源：`docker stats`

---

## 🎯 性能优化建议

基于测试结果，以下是常见的优化方向：

### 后端优化

1. **添加缓存层** (Redis)
   - 缓存用户 session
   - 缓存项目元数据
   - 缓存 LLM 配置

2. **数据库优化**
   - 添加索引
   - 优化查询
   - 使用连接池

3. **异步处理**
   - 代码质量检查改为异步任务
   - 模板应用改为后台任务
   - 使用 Celery + Redis

4. **响应压缩**
   - 启用 Gzip
   - 优化 JSON 序列化

### 前端优化

1. **代码分割**
   - 路由懒加载
   - 组件懒加载

2. **资源优化**
   - 图片压缩
   - 使用 CDN
   - 启用浏览器缓存

### 基础设施优化

1. **负载均衡**
   - Nginx 反向代理
   - 多实例部署

2. **水平扩展**
   - Docker Compose 多副本
   - Kubernetes 自动伸缩

---

## 📚 参考资源

### Locust 文档
- [官方文档](https://docs.locust.io/)
- [编写测试用例](https://docs.locust.io/en/stable/writing-a-locustfile.html)
- [命令行参数](https://docs.locust.io/en/stable/configuration.html)

### Socket.IO
- [Python Client](https://python-socketio.readthedocs.io/)
- [性能调优](https://socket.io/docs/v4/performance-tuning/)

### 性能测试最佳实践
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [性能测试指南](https://martinfowler.com/articles/practical-test-pyramid.html)

---

## 📞 支持

如遇到问题，请：
1. 查看本文档的故障排查部分
2. 提交 GitHub Issue
3. 联系: softctwo@aliyun.com

---

**版本**: 1.0
**更新日期**: 2025-11-14
**维护者**: Claude
