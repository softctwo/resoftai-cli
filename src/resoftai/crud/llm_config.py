"""CRUD operations for LLM configurations."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from resoftai.models.llm_config import LLMConfigModel


async def get_llm_config(
    db: AsyncSession,
    config_id: int
) -> Optional[LLMConfigModel]:
    """Get LLM config by ID."""
    result = await db.execute(
        select(LLMConfigModel).where(LLMConfigModel.id == config_id)
    )
    return result.scalar_one_or_none()


async def get_llm_configs_by_user(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[LLMConfigModel]:
    """Get all LLM configs for a user."""
    result = await db.execute(
        select(LLMConfigModel)
        .where(LLMConfigModel.user_id == user_id)
        .order_by(LLMConfigModel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_active_llm_config(
    db: AsyncSession,
    user_id: int
) -> Optional[LLMConfigModel]:
    """Get the active LLM config for a user."""
    result = await db.execute(
        select(LLMConfigModel).where(
            LLMConfigModel.user_id == user_id,
            LLMConfigModel.is_active == True
        )
    )
    return result.scalar_one_or_none()


async def create_llm_config(
    db: AsyncSession,
    user_id: int,
    provider: str,
    model: str,
    api_key: str,
    api_base: Optional[str] = None,
    max_tokens: int = 8192,
    temperature: float = 0.7,
    top_p: float = 0.95,
    is_active: bool = False
) -> LLMConfigModel:
    """Create a new LLM configuration."""
    # If setting as active, deactivate all other configs
    if is_active:
        await deactivate_all_configs(db, user_id)

    config = LLMConfigModel(
        user_id=user_id,
        provider=provider,
        model=model,
        api_key=api_key,
        api_base=api_base,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        is_active=is_active
    )

    db.add(config)
    await db.flush()
    await db.refresh(config)

    return config


async def update_llm_config(
    db: AsyncSession,
    config_id: int,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    is_active: Optional[bool] = None
) -> Optional[LLMConfigModel]:
    """Update LLM configuration."""
    config = await get_llm_config(db, config_id)

    if not config:
        return None

    # If setting as active, deactivate all other configs
    if is_active is True:
        await deactivate_all_configs(db, config.user_id)

    # Update fields
    if model is not None:
        config.model = model

    if api_key is not None:
        config.api_key = api_key

    if api_base is not None:
        config.api_base = api_base

    if max_tokens is not None:
        config.max_tokens = max_tokens

    if temperature is not None:
        config.temperature = temperature

    if top_p is not None:
        config.top_p = top_p

    if is_active is not None:
        config.is_active = is_active

    await db.flush()
    await db.refresh(config)

    return config


async def delete_llm_config(
    db: AsyncSession,
    config_id: int
) -> bool:
    """Delete LLM configuration."""
    config = await get_llm_config(db, config_id)

    if not config:
        return False

    await db.delete(config)
    await db.flush()

    return True


async def activate_config(
    db: AsyncSession,
    config_id: int
) -> Optional[LLMConfigModel]:
    """Activate a specific LLM config (deactivates all others for the user)."""
    config = await get_llm_config(db, config_id)

    if not config:
        return None

    # Deactivate all other configs
    await deactivate_all_configs(db, config.user_id)

    # Activate this config
    config.is_active = True

    await db.flush()
    await db.refresh(config)

    return config


async def deactivate_all_configs(
    db: AsyncSession,
    user_id: int
) -> None:
    """Deactivate all LLM configs for a user."""
    from sqlalchemy import update

    await db.execute(
        update(LLMConfigModel)
        .where(LLMConfigModel.user_id == user_id)
        .values(is_active=False)
    )

    await db.flush()


async def count_user_llm_configs(
    db: AsyncSession,
    user_id: int
) -> int:
    """Count LLM configs for a user."""
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(LLMConfigModel.id)).where(
            LLMConfigModel.user_id == user_id
        )
    )
    return result.scalar_one()
