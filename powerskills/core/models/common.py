"""通用模型和枚举"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """用户角色"""

    FREE = "free"
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class PlatformType(str, Enum):
    """平台类型"""

    COZE = "coze"
    DIFY = "dify"
    LANGCHAIN = "langchain"
    CURSOR = "cursor"
    GITHUB = "github"
    CUSTOM = "custom"


class SubscriptionStatus(str, Enum):
    """订阅状态"""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"


class ExecutionStatus(str, Enum):
    """执行状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Pricing(BaseModel):
    """定价模型"""

    type: str = "free"  # free, subscription, per_use
    price: Optional[float] = None
    currency: str = "USD"


class Pagination(BaseModel):
    """分页信息"""

    page: int = 1
    limit: int = 20
    total: int = 0
    total_pages: int = 0


class ErrorDetail(BaseModel):
    """错误详情"""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""

    error: ErrorDetail


class ListResponse(BaseModel):
    """列表响应"""

    data: List[Any]
    pagination: Pagination
