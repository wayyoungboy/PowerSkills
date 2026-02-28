"""编排路由"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from powerskills.core.models.orchestration import Orchestration, OrchestrationCreate
from powerskills.core.models.common import ListResponse
from powerskills.core.models.user import User
from powerskills.core.services.orchestration import orchestration_service
from powerskills.api.routes.auth import get_current_user

router = APIRouter(prefix="/orchestrations", tags=["技能编排"])


@router.post("", response_model=Orchestration, status_code=status.HTTP_201_CREATED)
async def create_orchestration(
    orchestration_data: OrchestrationCreate, current_user: User = Depends(get_current_user)
):
    """创建编排计划"""
    orchestration = await orchestration_service.create_plan(
        user_id=current_user.user_id, task_data=orchestration_data
    )
    return orchestration


@router.get("", response_model=ListResponse)
async def list_orchestrations(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
):
    """获取编排计划列表"""
    plans, _ = await orchestration_service.list_plans(
        user_id=current_user.user_id, page=page, limit=limit
    )

    return ListResponse(
        data=[p.model_dump() for p in plans],
        pagination={
            "page": page,
            "limit": limit,
            "total": len(plans),
            "total_pages": (len(plans) + limit - 1) // limit if limit > 0 else 0,
        },
    )


@router.get("/{plan_id}", response_model=Orchestration)
async def get_orchestration(plan_id: str, current_user: User = Depends(get_current_user)):
    """获取编排计划详情"""
    orchestration = await orchestration_service.get_plan(plan_id)
    if not orchestration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="编排计划不存在")

    return orchestration


@router.post("/{plan_id}/execute", response_model=Orchestration)
async def execute_orchestration(plan_id: str, current_user: User = Depends(get_current_user)):
    """执行编排计划"""
    try:
        orchestration = await orchestration_service.execute_plan(plan_id)
        return orchestration
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{plan_id}")
async def cancel_orchestration(plan_id: str, current_user: User = Depends(get_current_user)):
    """取消编排计划"""
    success = await orchestration_service.cancel_plan(plan_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无法取消编排计划")

    return {"message": "编排计划已取消"}
