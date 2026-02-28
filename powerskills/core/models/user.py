"""用户模型"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from .common import UserRole


class UserBase(BaseModel):
    """用户基础模型"""

    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """用户创建请求"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """用户更新请求"""

    name: Optional[str] = None
    avatar_url: Optional[str] = None


class User(UserBase):
    """用户响应模型"""

    user_id: str = Field(default_factory=lambda: f"usr_{__import__('uuid').uuid4().hex[:12]}")
    role: UserRole = UserRole.FREE
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
