# 安全修复建议与实现

## 紧急修复项（P0）

### 1. 代码分析API - 路径遍历防护

#### 当前问题
```python
# ❌ 不安全
temp_file = Path(tmpdir) / f"{filename}.py"
# filename 可以是 "../../../etc/passwd"
```

#### 修复方案
```python
import re
from pathlib import Path

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename to prevent path traversal and injection.

    Args:
        filename: Original filename from user
        max_length: Maximum allowed filename length

    Returns:
        Safe filename containing only alphanumeric, dash, underscore, and dot

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("test<script>.py")
        'test_script_.py'
    """
    # Remove path components
    filename = Path(filename).name

    # Remove dangerous characters
    filename = re.sub(r'[^\w\-.]', '_', filename)

    # Remove consecutive dots (to prevent ..)
    filename = re.sub(r'\.{2,}', '.', filename)

    # Ensure it doesn't start with dot
    filename = filename.lstrip('.')

    # Limit length
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:max_length - len(ext) - 1] + '.' + ext if ext else name[:max_length]

    # Default if empty
    return filename or 'temp'

# 使用示例
temp_file = Path(tmpdir) / f"{sanitize_filename(filename)}.py"
```

---

### 2. 代码分析API - 超时和资源限制

#### 修复方案
```python
import asyncio
from asyncio import Semaphore

# 全局并发限制
_analysis_semaphore = Semaphore(5)  # 最多5个并发分析

# 配置
ANALYSIS_TIMEOUT = 30  # 秒
MAX_CODE_SIZE = 100_000  # 字符

class CodeAnalysisRequest(BaseModel):
    """Request for code analysis."""
    code: str = Field(
        ...,
        description="Code content to analyze",
        max_length=MAX_CODE_SIZE
    )
    language: str = Field(..., description="Programming language")
    filename: str = Field(default="temp", description="Filename")
    tools: List[str] = Field(default=["all"])


async def run_pylint_safe(code: str, filename: str) -> Dict:
    """
    Run pylint with timeout and error handling.

    Raises:
        HTTPException: On timeout or execution error
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        temp_file = Path(tmpdir) / f"{safe_filename}.py"
        temp_file.write_text(code, encoding='utf-8')

        try:
            # Create subprocess with timeout
            process = await asyncio.create_subprocess_exec(
                'pylint',
                str(temp_file),
                '--output-format=json',
                '--rcfile=.pylintrc',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=ANALYSIS_TIMEOUT
                )
            except asyncio.TimeoutError:
                # Kill the process
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                raise HTTPException(
                    status_code=408,
                    detail=f"Analysis timeout after {ANALYSIS_TIMEOUT} seconds"
                )

            # Process results...
            issues = []
            score = None

            if stdout:
                try:
                    pylint_output = json.loads(stdout.decode())
                    for issue in pylint_output:
                        issues.append(AnalysisIssue(
                            line=issue.get('line'),
                            column=issue.get('column'),
                            severity='error' if issue.get('type') == 'error' else 'warning',
                            message=issue.get('message', ''),
                            rule=issue.get('message-id'),
                            tool='pylint'
                        ))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse pylint output: {e}")

            return {
                'success': True,
                'issues': issues,
                'score': score
            }

        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail="Analysis tool not available"
            )
        except Exception as e:
            logger.error(f"Pylint execution error: {e}", exc_info=True)
            # Don't expose internal error details
            raise HTTPException(
                status_code=500,
                detail="Analysis failed due to internal error"
            )


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze code with rate limiting and resource control.
    """
    import time

    # Rate limiting per user (requires Redis in production)
    # For now, use semaphore for global concurrency control
    async with _analysis_semaphore:
        start_time = time.time()

        all_issues = []
        score = None

        # Determine tools
        tools = request.tools
        if "all" in tools:
            if request.language.lower() == "python":
                tools = ["pylint", "mypy"]
            elif request.language.lower() in ["javascript", "typescript"]:
                tools = ["eslint"]
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported language: {request.language}"
                )

        # Run analysis
        if request.language.lower() == "python":
            if "pylint" in tools:
                result = await run_pylint_safe(request.code, request.filename)
                all_issues.extend(result['issues'])
                if result.get('score') is not None:
                    score = result['score']

            if "mypy" in tools:
                result = await run_mypy_safe(request.code, request.filename)
                all_issues.extend(result['issues'])

        elif request.language.lower() in ["javascript", "typescript"]:
            if "eslint" in tools:
                result = await run_eslint_safe(request.code, request.filename)
                all_issues.extend(result['issues'])

        # Calculate summary
        summary = {
            'error': sum(1 for issue in all_issues if issue.severity == 'error'),
            'warning': sum(1 for issue in all_issues if issue.severity == 'warning'),
            'info': sum(1 for issue in all_issues if issue.severity == 'info')
        }

        execution_time = time.time() - start_time

        return CodeAnalysisResponse(
            success=True,
            language=request.language,
            issues=all_issues,
            summary=summary,
            score=score,
            execution_time=execution_time
        )
```

---

### 3. 实时协作 - 权限验证

#### 修复方案
```python
from resoftai.crud.file import get_file
from resoftai.crud.project import get_project_by_id
from resoftai.db import get_async_session

async def verify_file_access(file_id: int, user_id: int) -> bool:
    """
    Verify if user has access to the file.

    Args:
        file_id: File ID to check
        user_id: User ID requesting access

    Returns:
        True if access granted, False otherwise
    """
    try:
        async for db in get_async_session():
            # Get file
            file = await get_file(db, file_id)
            if not file:
                return False

            # Get project
            project = await get_project_by_id(db, file.project_id)
            if not project:
                return False

            # Check ownership
            if project.user_id == user_id:
                return True

            # TODO: Check collaborator permissions from project members table
            # For now, only owner has access
            return False

    except Exception as e:
        logger.error(f"Error verifying file access: {e}")
        return False


@sio.event
async def join_file_editing(sid, data):
    """
    Join a file editing session with permission check.
    """
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    username = data.get('username', f'User {user_id}')

    if not file_id or not user_id:
        await sio.emit('error', {
            'message': 'Missing file_id or user_id'
        }, room=sid)
        return

    # ✅ SECURITY: Verify access permission
    has_access = await verify_file_access(file_id, user_id)
    if not has_access:
        await sio.emit('error', {
            'message': 'Permission denied - you do not have access to this file'
        }, room=sid)
        logger.warning(f"User {user_id} attempted unauthorized access to file {file_id}")
        return

    # Track active editor
    if file_id not in active_editors:
        active_editors[file_id] = {}

    active_editors[file_id][user_id] = {
        'sid': sid,
        'username': username,
        'cursor_position': None,
        'selection': None,
        'joined_at': datetime.utcnow().isoformat()
    }

    # Join file room
    room = f"file:{file_id}"
    await sio.enter_room(sid, room)

    # Notify other editors
    await sio.emit('user_joined_file', {
        'file_id': file_id,
        'user_id': user_id,
        'username': username,
        'active_users': len(active_editors[file_id])
    }, room=room, skip_sid=sid)

    # Send current active users
    await sio.emit('file_editors_list', {
        'file_id': file_id,
        'editors': [
            {
                'user_id': uid,
                'username': info['username'],
                'cursor_position': info.get('cursor_position'),
                'selection': info.get('selection')
            }
            for uid, info in active_editors[file_id].items()
            if uid != user_id
        ]
    }, room=sid)

    logger.info(f"User {user_id} joined file {file_id} editing")
```

---

### 4. 实时协作 - 内存泄露防护

#### 修复方案
```python
from collections import OrderedDict
from datetime import datetime, timedelta
import asyncio

class LRUDict(OrderedDict):
    """
    LRU (Least Recently Used) cache with max size.
    """
    def __init__(self, maxsize=1000):
        self.maxsize = maxsize
        super().__init__()

    def __setitem__(self, key, value):
        if key in self:
            # Move to end
            del self[key]
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            # Remove oldest
            self.popitem(last=False)

    def __getitem__(self, key):
        # Move to end on access
        value = super().__getitem__(key)
        del self[key]
        super().__setitem__(key, value)
        return value


# Use LRU cache instead of dict
active_editors = LRUDict(maxsize=1000)  # Max 1000 active files
file_operations = LRUDict(maxsize=500)  # Max 500 file histories

# Session tracking for fast cleanup
sid_to_sessions: Dict[str, List[tuple]] = {}


async def cleanup_inactive_sessions():
    """
    Background task to clean up inactive editing sessions.

    Runs every hour to remove sessions inactive for > 1 hour.
    """
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour

            now = datetime.utcnow()
            cleaned_files = 0
            cleaned_users = 0

            for file_id in list(active_editors.keys()):
                for user_id in list(active_editors[file_id].keys()):
                    try:
                        joined_at_str = active_editors[file_id][user_id].get('joined_at')
                        if not joined_at_str:
                            continue

                        joined_at = datetime.fromisoformat(joined_at_str)
                        inactive_duration = now - joined_at

                        # Clean up if inactive for > 1 hour
                        if inactive_duration > timedelta(hours=1):
                            del active_editors[file_id][user_id]
                            cleaned_users += 1

                    except Exception as e:
                        logger.warning(f"Error cleaning user session: {e}")
                        continue

                # Clean empty file entries
                if file_id in active_editors and not active_editors[file_id]:
                    del active_editors[file_id]
                    cleaned_files += 1

            if cleaned_files > 0 or cleaned_users > 0:
                logger.info(
                    f"Cleaned up {cleaned_users} inactive users from {cleaned_files} files"
                )

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}", exc_info=True)


# Start cleanup task on module import
import asyncio
cleanup_task = asyncio.create_task(cleanup_inactive_sessions())


@sio.event
async def disconnect(sid):
    """
    Handle client disconnection with optimized cleanup.
    """
    logger.info(f"Client disconnected: {sid}")

    # Fast lookup using sid_to_sessions
    if sid in sid_to_sessions:
        for file_id, user_id in sid_to_sessions[sid]:
            try:
                if file_id in active_editors and user_id in active_editors[file_id]:
                    username = active_editors[file_id][user_id].get('username', 'Unknown')
                    del active_editors[file_id][user_id]

                    # Clean empty file entries
                    if not active_editors[file_id]:
                        del active_editors[file_id]

                    # Notify other users
                    room = f"file:{file_id}"
                    await sio.emit('user_left_file', {
                        'file_id': file_id,
                        'user_id': user_id,
                        'username': username,
                        'active_users': len(active_editors.get(file_id, {}))
                    }, room=room)

            except Exception as e:
                logger.warning(f"Error cleaning session for file {file_id}: {e}")

        del sid_to_sessions[sid]
```

---

### 5. 速率限制

#### 修复方案
```python
from collections import defaultdict
from time import time

# Rate limit tracking
_rate_limits: Dict[str, List[float]] = defaultdict(list)


def check_rate_limit(
    key: str,
    max_requests: int = 10,
    window: int = 1
) -> bool:
    """
    Check if request exceeds rate limit.

    Args:
        key: Identifier (e.g., user_id or sid)
        max_requests: Maximum requests allowed
        window: Time window in seconds

    Returns:
        True if within limit, False if exceeded
    """
    now = time()

    # Clean old timestamps
    _rate_limits[key] = [
        t for t in _rate_limits[key]
        if now - t < window
    ]

    # Check limit
    if len(_rate_limits[key]) >= max_requests:
        return False

    # Record request
    _rate_limits[key].append(now)
    return True


@sio.event
async def cursor_position_change(sid, data):
    """
    Update cursor position with rate limiting.
    """
    # Rate limit: 30 requests per second
    if not check_rate_limit(sid, max_requests=30, window=1):
        # Silently drop - too many cursor updates
        return

    file_id = data.get('file_id')
    user_id = data.get('user_id')
    position = data.get('position')
    selection = data.get('selection')

    if not file_id or not user_id or not position:
        return

    # Update cursor position
    if file_id in active_editors and user_id in active_editors[file_id]:
        active_editors[file_id][user_id]['cursor_position'] = position
        active_editors[file_id][user_id]['selection'] = selection

        # Broadcast
        room = f"file:{file_id}"
        await sio.emit('cursor_position_changed', {
            'file_id': file_id,
            'user_id': user_id,
            'username': active_editors[file_id][user_id].get('username'),
            'position': position,
            'selection': selection
        }, room=room, skip_sid=sid)


@sio.event
async def file_content_change(sid, data):
    """
    Handle file content changes with rate limiting.
    """
    # Rate limit: 10 changes per second
    if not check_rate_limit(sid, max_requests=10, window=1):
        await sio.emit('error', {
            'message': 'Rate limit exceeded - too many requests'
        }, room=sid)
        return

    # Continue processing...
    file_id = data.get('file_id')
    user_id = data.get('user_id')
    changes = data.get('changes', [])
    version = data.get('version', 0)

    if not file_id or not user_id:
        return

    # Store operation
    if file_id not in file_operations:
        file_operations[file_id] = []

    operation = {
        'user_id': user_id,
        'changes': changes,
        'version': version,
        'timestamp': datetime.utcnow().isoformat()
    }
    file_operations[file_id].append(operation)

    # Keep only last 100 operations
    if len(file_operations[file_id]) > 100:
        file_operations[file_id] = file_operations[file_id][-100:]

    # Broadcast
    room = f"file:{file_id}"
    await sio.emit('file_content_changed', {
        'file_id': file_id,
        'user_id': user_id,
        'changes': changes,
        'version': version,
        'timestamp': operation['timestamp']
    }, room=room, skip_sid=sid)
```

---

## 实施计划

### 第1天（今天）
1. ✅ 实现 `sanitize_filename()` 函数
2. ✅ 添加超时保护到所有分析函数
3. ✅ 添加代码大小限制

### 第2天
4. 实现权限验证
5. 添加速率限制
6. 实现LRU缓存

### 第3天
7. 测试所有修复
8. 更新文档
9. 部署到测试环境

### 第4-5天
10. 监控和调优
11. 修复发现的问题
12. 准备生产部署

---

## 测试清单

- [ ] 路径遍历攻击测试
- [ ] 超大文件测试
- [ ] 超时场景测试
- [ ] 并发压力测试
- [ ] 权限验证测试
- [ ] 速率限制测试
- [ ] 内存泄露检查
- [ ] 断线重连测试

---

## 监控指标

需要添加的监控：

```python
from prometheus_client import Counter, Histogram, Gauge

# 静态分析
analysis_requests_total = Counter('analysis_requests_total', 'Total analysis requests', ['language', 'tool'])
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration', ['language', 'tool'])
analysis_timeouts = Counter('analysis_timeouts_total', 'Total timeouts', ['language'])
analysis_errors = Counter('analysis_errors_total', 'Total errors', ['language', 'error_type'])

# 实时协作
active_files_gauge = Gauge('collaboration_active_files', 'Number of files being edited')
active_users_gauge = Gauge('collaboration_active_users', 'Number of active editing users')
collaboration_events = Counter('collaboration_events_total', 'Total collaboration events', ['event_type'])
rate_limit_hits = Counter('collaboration_rate_limit_hits', 'Rate limit violations', ['event_type'])
```

---

## 部署检查清单

生产环境部署前确认：

- [ ] 所有P0问题已修复
- [ ] 单元测试全部通过
- [ ] 安全扫描通过
- [ ] 性能测试通过
- [ ] 监控和告警已配置
- [ ] 文档已更新
- [ ] 回滚方案已准备
- [ ] 团队已培训

---

**版本**: v0.2.1-security
**日期**: 2025-01-14
**优先级**: P0 (紧急)
