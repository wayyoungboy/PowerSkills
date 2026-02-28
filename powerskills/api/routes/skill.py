"""技能路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from powerskills.core.models.skill import (
    Skill,
    SkillCreate,
    SkillUpdate,
    SkillSearchResult,
)
from powerskills.core.models.common import PlatformType, Pagination, ListResponse
from powerskills.core.models.user import User
from powerskills.core.services.skill import skill_service
from powerskills.api.routes.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["技能管理"])


@router.get("", response_model=ListResponse)
async def list_skills(
    platform: Optional[PlatformType] = Query(None, description="平台筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
):
    """获取技能列表"""
    skills, pagination = await skill_service.list_skills(platform=platform, page=page, limit=limit)

    return ListResponse(data=[s.model_dump() for s in skills], pagination=pagination)


@router.get("/search", response_model=List[SkillSearchResult])
async def search_skills(
    q: str = Query(..., description="搜索关键词"),
    platforms: Optional[List[PlatformType]] = Query(None, description="平台筛选"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
):
    """搜索技能"""
    results = await skill_service.search_skills(
        query=q, platforms=platforms, page=page, limit=limit
    )

    return results


@router.get("/{skill_id}", response_model=Skill)
async def get_skill(skill_id: str, current_user: User = Depends(get_current_user)):
    """获取技能详情"""
    skill = await skill_service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="技能不存在")

    return skill


@router.post("", response_model=Skill, status_code=status.HTTP_201_CREATED)
async def create_skill(skill_data: SkillCreate, current_user: User = Depends(get_current_user)):
    """创建技能"""
    skill = await skill_service.create_skill(skill_data, current_user.user_id)
    return skill


@router.put("/{skill_id}", response_model=Skill)
async def update_skill(
    skill_id: str, skill_data: SkillUpdate, current_user: User = Depends(get_current_user)
):
    """更新技能"""
    skill = await skill_service.update_skill(skill_id, skill_data)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="技能不存在")

    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str, current_user: User = Depends(get_current_user)):
    """删除技能"""
    success = await skill_service.delete_skill(skill_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="技能不存在")
