"""
Plugin Review Workflow

插件审核流程管理
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.plugin import Plugin, PluginStatus
from resoftai.crud.plugin import get_plugin_by_id, update_plugin


class ReviewDecision:
    """审核决定"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"


async def submit_for_review(
    db: AsyncSession,
    plugin_id: int
) -> bool:
    """
    提交插件供审核

    Args:
        db: 数据库会话
        plugin_id: 插件ID

    Returns:
        是否成功
    """
    plugin = await get_plugin_by_id(db, plugin_id)

    if not plugin:
        return False

    if plugin.status not in [PluginStatus.DRAFT, PluginStatus.REJECTED]:
        return False

    # 更新状态
    await update_plugin(db, plugin_id, status=PluginStatus.SUBMITTED)

    return True


async def get_pending_reviews(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20
) -> List[Plugin]:
    """
    获取待审核的插件列表

    Args:
        db: 数据库会话
        skip: 跳过数量
        limit: 限制数量

    Returns:
        待审核插件列表
    """
    query = select(Plugin).where(
        Plugin.status == PluginStatus.SUBMITTED
    ).order_by(desc(Plugin.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def review_plugin(
    db: AsyncSession,
    plugin_id: int,
    decision: str,
    reviewer_id: int,
    comments: Optional[str] = None,
    required_changes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    审核插件

    Args:
        db: 数据库会话
        plugin_id: 插件ID
        decision: 审核决定 (approved/rejected/needs_changes)
        reviewer_id: 审核人ID
        comments: 审核意见
        required_changes: 需要的更改（如果决定是needs_changes）

    Returns:
        审核结果
    """
    plugin = await get_plugin_by_id(db, plugin_id)

    if not plugin:
        return {"success": False, "error": "Plugin not found"}

    if plugin.status != PluginStatus.SUBMITTED:
        return {"success": False, "error": "Plugin is not in submitted status"}

    # 根据决定更新状态
    if decision == ReviewDecision.APPROVED:
        new_status = PluginStatus.APPROVED
        plugin.published_at = datetime.utcnow()
    elif decision == ReviewDecision.REJECTED:
        new_status = PluginStatus.REJECTED
    elif decision == ReviewDecision.NEEDS_CHANGES:
        new_status = PluginStatus.DRAFT
    else:
        return {"success": False, "error": "Invalid decision"}

    # 更新插件
    await update_plugin(db, plugin_id, status=new_status)

    # 创建审核记录
    review_record = {
        "plugin_id": plugin_id,
        "reviewer_id": reviewer_id,
        "decision": decision,
        "comments": comments,
        "required_changes": required_changes or [],
        "reviewed_at": datetime.utcnow().isoformat()
    }

    # 在实际应用中，这里会保存到审核记录表
    # await create_review_record(db, review_record)

    # 发送通知给插件作者
    # await notify_plugin_author(plugin.author_id, review_record)

    return {
        "success": True,
        "decision": decision,
        "new_status": new_status.value,
        "review_record": review_record
    }


async def run_automated_checks(
    db: AsyncSession,
    plugin_id: int
) -> Dict[str, Any]:
    """
    运行自动化检查

    Args:
        db: 数据库会话
        plugin_id: 插件ID

    Returns:
        检查结果
    """
    plugin = await get_plugin_by_id(db, plugin_id)

    if not plugin:
        return {"success": False, "error": "Plugin not found"}

    issues = []
    warnings = []
    passed_checks = []

    # 1. 检查必需字段
    required_fields = {
        "name": plugin.name,
        "description": plugin.description,
        "version": plugin.version,
        "author_name": plugin.author_name,
        "package_url": plugin.package_url,
        "license": plugin.license
    }

    for field, value in required_fields.items():
        if not value:
            issues.append({
                "check": f"required_field_{field}",
                "severity": "error",
                "message": f"缺少必需字段: {field}"
            })
        else:
            passed_checks.append(f"required_field_{field}")

    # 2. 检查描述长度
    if plugin.description and len(plugin.description) < 20:
        warnings.append({
            "check": "description_length",
            "severity": "warning",
            "message": "描述太短，建议至少20个字符"
        })
    else:
        passed_checks.append("description_length")

    # 3. 检查版本格式
    if plugin.version:
        import re
        if not re.match(r"^\d+\.\d+\.\d+", plugin.version):
            issues.append({
                "check": "version_format",
                "severity": "error",
                "message": "版本号格式无效，应为 X.Y.Z"
            })
        else:
            passed_checks.append("version_format")

    # 4. 检查标签
    if not plugin.tags or len(plugin.tags) == 0:
        warnings.append({
            "check": "tags",
            "severity": "warning",
            "message": "建议添加至少一个标签以提高可发现性"
        })
    else:
        passed_checks.append("tags")

    # 5. 检查文档链接
    if not plugin.documentation_url:
        warnings.append({
            "check": "documentation",
            "severity": "warning",
            "message": "建议提供文档链接"
        })
    else:
        passed_checks.append("documentation")

    # 6. 检查图标
    if not plugin.icon_url:
        warnings.append({
            "check": "icon",
            "severity": "warning",
            "message": "建议上传插件图标"
        })
    else:
        passed_checks.append("icon")

    # 7. 安全检查
    if plugin.package_url and not plugin.package_checksum:
        issues.append({
            "check": "security_checksum",
            "severity": "error",
            "message": "缺少package_checksum，存在安全风险"
        })
    else:
        passed_checks.append("security_checksum")

    # 计算得分
    total_checks = len(passed_checks) + len(issues) + len(warnings)
    score = (len(passed_checks) / total_checks * 100) if total_checks > 0 else 0

    can_approve = len(issues) == 0  # 只要没有错误就可以批准

    return {
        "success": True,
        "score": round(score, 2),
        "can_approve": can_approve,
        "total_checks": total_checks,
        "passed_checks": len(passed_checks),
        "issues_count": len(issues),
        "warnings_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
        "passed": passed_checks,
        "summary": _generate_check_summary(score, issues, warnings)
    }


def _generate_check_summary(
    score: float,
    issues: List[Dict],
    warnings: List[Dict]
) -> str:
    """生成检查摘要"""
    if len(issues) > 0:
        return f"发现 {len(issues)} 个错误，必须修复才能发布"
    elif len(warnings) > 0:
        return f"检查通过（得分: {score:.1f}/100），但有 {len(warnings)} 个建议改进项"
    else:
        return f"所有检查通过（得分: {score:.1f}/100），可以发布"


async def get_review_statistics(
    db: AsyncSession,
    days: int = 30
) -> Dict[str, Any]:
    """
    获取审核统计

    Args:
        db: 数据库会话
        days: 统计天数

    Returns:
        统计数据
    """
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # 统计各状态的插件数量
    status_counts = {}
    for status in PluginStatus:
        query = select(Plugin).where(
            and_(
                Plugin.status == status,
                Plugin.created_at >= cutoff_date
            )
        )
        result = await db.execute(query)
        status_counts[status.value] = len(result.scalars().all())

    # 待审核数量
    pending_query = select(Plugin).where(Plugin.status == PluginStatus.SUBMITTED)
    pending_result = await db.execute(pending_query)
    pending_count = len(pending_result.scalars().all())

    # 通过率
    total_reviewed = status_counts.get(PluginStatus.APPROVED.value, 0) + \
                    status_counts.get(PluginStatus.REJECTED.value, 0)

    approval_rate = 0
    if total_reviewed > 0:
        approval_rate = (status_counts.get(PluginStatus.APPROVED.value, 0) / total_reviewed) * 100

    return {
        "period_days": days,
        "pending_review": pending_count,
        "status_breakdown": status_counts,
        "total_reviewed": total_reviewed,
        "approval_rate": round(approval_rate, 2),
        "average_review_time_hours": 24  # TODO: 计算实际平均审核时间
    }
