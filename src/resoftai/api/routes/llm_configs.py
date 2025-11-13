"""API routes for LLM configurations."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from resoftai.db import get_db
from resoftai.auth.dependencies import get_current_active_user
from resoftai.models.user import User
from resoftai.models.llm_config import LLMConfigModel
from resoftai.crud import llm_config as crud
from resoftai.llm.factory import LLMFactory
from resoftai.llm.base import LLMConfig, ModelProvider


router = APIRouter(prefix="/llm-configs", tags=["llm-configs"])


# Pydantic schemas

class LLMConfigCreate(BaseModel):
    """Schema for creating LLM config."""
    name: Optional[str] = None
    provider: str
    model_name: str
    api_key: str
    api_base: Optional[str] = None
    max_tokens: int = 8192
    temperature: float = 0.7
    top_p: float = 0.95
    is_active: bool = False


class LLMConfigUpdate(BaseModel):
    """Schema for updating LLM config."""
    name: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    is_active: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    """Schema for LLM config response (masks API key)."""
    id: int
    user_id: int
    name: Optional[str]
    provider: str
    model_name: str
    api_key_masked: str
    api_base: Optional[str]
    max_tokens: int
    temperature: float
    top_p: float
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, config: LLMConfigModel):
        # Mask API key (show first 6 and last 4 characters)
        api_key = config.api_key_encrypted
        if len(api_key) > 10:
            masked_key = f"{api_key[:6]}...{api_key[-4:]}"
        else:
            masked_key = "***"

        return cls(
            id=config.id,
            user_id=config.user_id,
            name=config.name,
            provider=config.provider,
            model_name=config.model_name,
            api_key_masked=masked_key,
            api_base=None,  # Not in database model
            max_tokens=config.max_tokens or 8192,
            temperature=config.temperature or 0.7,
            top_p=0.95,  # Not in database model, use default
            is_active=config.is_default,
            created_at=config.created_at.isoformat()
        )


class LLMConfigListResponse(BaseModel):
    """Schema for LLM config list response."""
    configs: List[LLMConfigResponse]
    total: int
    skip: int
    limit: int


class LLMTestRequest(BaseModel):
    """Schema for testing LLM connection."""
    prompt: str = "Hello, please respond with 'OK' if you can understand me."


class LLMTestResponse(BaseModel):
    """Schema for LLM test response."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    tokens_used: Optional[int] = None


# Endpoints

@router.get("", response_model=LLMConfigListResponse)
async def list_llm_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's LLM configurations."""
    configs = await crud.get_llm_configs_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    total = await crud.count_user_llm_configs(db, current_user.id)

    return LLMConfigListResponse(
        configs=[LLMConfigResponse.from_orm(c) for c in configs],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/active", response_model=Optional[LLMConfigResponse])
async def get_active_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the currently active LLM configuration."""
    config = await crud.get_active_llm_config(db, current_user.id)

    if not config:
        return None

    return LLMConfigResponse.from_orm(config)


@router.get("/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get LLM configuration by ID."""
    config = await crud.get_llm_config(db, config_id)

    if not config:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # Verify ownership
    if config.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this config"
        )

    return LLMConfigResponse.from_orm(config)


@router.post("", response_model=LLMConfigResponse, status_code=201)
async def create_llm_config(
    config_data: LLMConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new LLM configuration."""
    # Validate provider
    try:
        ModelProvider(config_data.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {config_data.provider}"
        )

    config = await crud.create_llm_config(
        db,
        user_id=current_user.id,
        name=config_data.name,
        provider=config_data.provider,
        model_name=config_data.model_name,
        api_key=config_data.api_key,
        api_base=config_data.api_base,
        max_tokens=config_data.max_tokens,
        temperature=config_data.temperature,
        top_p=config_data.top_p,
        is_active=config_data.is_active
    )

    await db.commit()

    return LLMConfigResponse.from_orm(config)


@router.put("/{config_id}", response_model=LLMConfigResponse)
async def update_llm_config(
    config_id: int,
    config_data: LLMConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update LLM configuration."""
    config = await crud.get_llm_config(db, config_id)

    if not config:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # Verify ownership
    if config.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this config"
        )

    config = await crud.update_llm_config(
        db,
        config_id=config_id,
        model=config_data.model,
        api_key=config_data.api_key,
        api_base=config_data.api_base,
        max_tokens=config_data.max_tokens,
        temperature=config_data.temperature,
        top_p=config_data.top_p,
        is_active=config_data.is_active
    )

    await db.commit()

    return LLMConfigResponse.from_orm(config)


@router.post("/{config_id}/activate", response_model=LLMConfigResponse)
async def activate_llm_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a specific LLM configuration."""
    config = await crud.get_llm_config(db, config_id)

    if not config:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # Verify ownership
    if config.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to modify this config"
        )

    config = await crud.activate_config(db, config_id)

    await db.commit()

    return LLMConfigResponse.from_orm(config)


@router.delete("/{config_id}", status_code=204)
async def delete_llm_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete LLM configuration."""
    config = await crud.get_llm_config(db, config_id)

    if not config:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # Verify ownership
    if config.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this config"
        )

    # Don't allow deleting the active config if it's the only one
    if config.is_active:
        total = await crud.count_user_llm_configs(db, current_user.id)
        if total == 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the only active LLM configuration"
            )

    await crud.delete_llm_config(db, config_id)
    await db.commit()

    return None


@router.post("/{config_id}/test", response_model=LLMTestResponse)
async def test_llm_connection(
    config_id: int,
    test_request: LLMTestRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Test LLM configuration by making a simple API call."""
    config = await crud.get_llm_config(db, config_id)

    if not config:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # Verify ownership
    if config.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to use this config"
        )

    try:
        # Create LLM config
        llm_config = LLMConfig(
            provider=ModelProvider(config.provider),
            api_key=config.api_key,
            model_name=config.model_name,
            api_base=config.api_base,
            max_tokens=min(config.max_tokens, 100),  # Limit tokens for test
            temperature=config.temperature,
            top_p=config.top_p
        )

        # Create LLM instance
        llm = LLMFactory.create(llm_config)

        # Make test call
        response = await llm.generate(prompt=test_request.prompt)

        return LLMTestResponse(
            success=True,
            response=response.content,
            tokens_used=response.usage.get('total_tokens', 0)
        )

    except Exception as e:
        return LLMTestResponse(
            success=False,
            error=str(e)
        )
