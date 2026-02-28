"""认证模型"""

from typing import List

from pydantic import BaseModel, Field, EmailStr

from .common import UserRole


class Token(BaseModel):
    """Token 响应"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """Token 载荷"""

    sub: str  # user_id
    email: str
    role: UserRole
    permissions: List[str] = []


class LoginRequest(BaseModel):
    """登录请求"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = None
