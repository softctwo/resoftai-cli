"""
Plugin Update Notification System

插件更新检查和通知功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from packaging import version as pkg_version

from resoftai.models.plugin import (
    Plugin, PluginVersion, PluginInstallation,
    PluginStatus, InstallationStatus
)
from resoftai.crud.plugin import get_plugin_by_id


async def check_plugin_updates(
    db: AsyncSession,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    检查已安装插件的更新

    Args:
        db: 数据库会话
        user_id: 用户ID
        organization_id: 组织ID

    Returns:
        更新列表，包含插件信息和新版本
    """
    # 获取用户/组织的所有安装
    query = select(PluginInstallation).where(
        PluginInstallation.status == InstallationStatus.ACTIVE
    )

    if user_id:
        query = query.where(PluginInstallation.user_id == user_id)
    if organization_id:
        query = query.where(PluginInstallation.organization_id == organization_id)

    result = await db.execute(query)
    installations = result.scalars().all()

    updates = []

    for installation in installations:
        # 获取插件信息
        plugin = await get_plugin_by_id(db, installation.plugin_id)

        if not plugin:
            continue

        # 检查是否有更新
        current_version = pkg_version.parse(installation.installed_version)
        latest_version = pkg_version.parse(plugin.version)

        if latest_version > current_version:
            # 获取版本历史
            changelog = await _get_version_changelog(
                db,
                plugin.id,
                installation.installed_version,
                plugin.version
            )

            updates.append({
                "plugin_id": plugin.id,
                "plugin_name": plugin.name,
                "plugin_slug": plugin.slug,
                "current_version": installation.installed_version,
                "latest_version": plugin.version,
                "update_type": _determine_update_type(
                    installation.installed_version,
                    plugin.version
                ),
                "changelog": changelog,
                "is_breaking": _is_breaking_change(changelog),
                "installation_id": installation.id
            })

    return updates


async def _get_version_changelog(
    db: AsyncSession,
    plugin_id: int,
    from_version: str,
    to_version: str
) -> List[Dict[str, Any]]:
    """获取版本之间的changelog"""
    query = select(PluginVersion).where(
        PluginVersion.plugin_id == plugin_id
    ).order_by(PluginVersion.created_at.desc())

    result = await db.execute(query)
    versions = result.scalars().all()

    changelog = []
    from_v = pkg_version.parse(from_version)
    to_v = pkg_version.parse(to_version)

    for ver in versions:
        v = pkg_version.parse(ver.version)
        if from_v < v <= to_v:
            changelog.append({
                "version": ver.version,
                "released_at": ver.created_at.isoformat() if ver.created_at else None,
                "changelog": ver.changelog,
                "is_stable": ver.is_stable
            })

    return changelog


def _determine_update_type(from_version: str, to_version: str) -> str:
    """
    确定更新类型（major, minor, patch）

    Args:
        from_version: 当前版本
        to_version: 新版本

    Returns:
        更新类型
    """
    from_v = pkg_version.parse(from_version)
    to_v = pkg_version.parse(to_version)

    # 简化的版本比较
    from_parts = str(from_v).split(".")
    to_parts = str(to_v).split(".")

    if len(from_parts) >= 1 and len(to_parts) >= 1:
        if from_parts[0] != to_parts[0]:
            return "major"

    if len(from_parts) >= 2 and len(to_parts) >= 2:
        if from_parts[1] != to_parts[1]:
            return "minor"

    return "patch"


def _is_breaking_change(changelog: List[Dict[str, Any]]) -> bool:
    """检查是否包含破坏性更新"""
    for entry in changelog:
        if entry.get("changelog"):
            # 检查changelog中是否包含破坏性更新关键词
            text = entry["changelog"].lower()
            breaking_keywords = [
                "breaking change",
                "breaking:",
                "不兼容",
                "破坏性更新",
                "migration required"
            ]
            if any(keyword in text for keyword in breaking_keywords):
                return True

    return False


async def update_plugin(
    db: AsyncSession,
    installation_id: int
) -> bool:
    """
    更新插件到最新版本

    Args:
        db: 数据库会话
        installation_id: 安装ID

    Returns:
        是否成功
    """
    result = await db.execute(
        select(PluginInstallation).where(PluginInstallation.id == installation_id)
    )
    installation = result.scalar_one_or_none()

    if not installation:
        return False

    # 获取最新版本
    plugin = await get_plugin_by_id(db, installation.plugin_id)

    if not plugin:
        return False

    # 更新安装记录
    installation.installed_version = plugin.version
    installation.status = InstallationStatus.UPDATING
    installation.updated_at = datetime.utcnow()

    await db.commit()

    # TODO: 触发实际的更新流程（下载、安装等）

    # 标记为已安装
    installation.status = InstallationStatus.ACTIVE
    await db.commit()

    return True


async def get_update_statistics(
    db: AsyncSession,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    获取更新统计信息

    Args:
        db: 数据库会话
        user_id: 用户ID
        organization_id: 组织ID

    Returns:
        统计信息
    """
    updates = await check_plugin_updates(db, user_id, organization_id)

    return {
        "total_updates": len(updates),
        "major_updates": len([u for u in updates if u["update_type"] == "major"]),
        "minor_updates": len([u for u in updates if u["update_type"] == "minor"]),
        "patch_updates": len([u for u in updates if u["update_type"] == "patch"]),
        "breaking_changes": len([u for u in updates if u["is_breaking"]]),
        "updates": updates
    }


async def enable_auto_update(
    db: AsyncSession,
    installation_id: int,
    auto_update: bool = True
) -> bool:
    """
    启用/禁用自动更新

    Args:
        db: 数据库会话
        installation_id: 安装ID
        auto_update: 是否自动更新

    Returns:
        是否成功
    """
    result = await db.execute(
        select(PluginInstallation).where(PluginInstallation.id == installation_id)
    )
    installation = result.scalar_one_or_none()

    if not installation:
        return False

    # 更新配置
    config = installation.config or {}
    config["auto_update"] = auto_update
    installation.config = config
    installation.updated_at = datetime.utcnow()

    await db.commit()

    return True


async def get_plugins_needing_update(
    db: AsyncSession,
    auto_update_only: bool = False
) -> List[PluginInstallation]:
    """
    获取需要更新的插件列表

    Args:
        db: 数据库会话
        auto_update_only: 只返回启用自动更新的插件

    Returns:
        需要更新的安装列表
    """
    query = select(PluginInstallation).where(
        PluginInstallation.status == InstallationStatus.ACTIVE
    )

    result = await db.execute(query)
    installations = result.scalars().all()

    needs_update = []

    for installation in installations:
        # 检查自动更新设置
        if auto_update_only:
            config = installation.config or {}
            if not config.get("auto_update", False):
                continue

        # 检查版本
        plugin = await get_plugin_by_id(db, installation.plugin_id)
        if not plugin:
            continue

        current_version = pkg_version.parse(installation.installed_version)
        latest_version = pkg_version.parse(plugin.version)

        if latest_version > current_version:
            needs_update.append(installation)

    return needs_update
