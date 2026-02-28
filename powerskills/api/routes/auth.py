"""认证路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from powerskills.core.models.auth import LoginRequest, RegisterRequest, Token
from powerskills.core.models.user import User
from powerskills.core.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])
security = HTTPBearer()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        user = await auth_service.register(
            email=request.email, password=request.password, name=request.name
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """用户登录"""
    try:
        token = await auth_service.login(email=request.email, password=request.password)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """刷新访问令牌"""
    try:
        token = await auth_service.refresh_access_token(credentials.credentials)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前用户"""
    payload = auth_service.decode_token(credentials.credentials)
    if not payload or not payload.sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")

    user = await auth_service.get_user(payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

    return user
