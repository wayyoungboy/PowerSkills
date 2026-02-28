"""API 路由"""

from fastapi import APIRouter

from powerskills.api.routes import auth, skill, orchestration

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(skill.router)
api_router.include_router(orchestration.router)
