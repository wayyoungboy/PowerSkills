"""SkillHub 数据模型

模型模块按功能划分：
- common: 通用模型和枚举（UserRole, PlatformType, Pricing, Pagination 等）
- user: 用户模型（User, UserCreate, UserUpdate）
- skill: 技能模型（Skill, SkillCreate, SkillUpdate, SkillSearchResult）
- orchestration: 编排模型（Orchestration, OrchestrationCreate, SkillChainStep）
- auth: 认证模型（Token, TokenPayload, LoginRequest, RegisterRequest）
"""

from .common import (
    UserRole,
    PlatformType,
    SubscriptionStatus,
    ExecutionStatus,
    Pricing,
    Pagination,
    ErrorDetail,
    ErrorResponse,
    ListResponse,
)

from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    User,
)

from .skill import (
    SkillBase,
    SkillCreate,
    SkillUpdate,
    Skill,
    SkillSearchResult,
)

from .orchestration import (
    SkillChainStep,
    OrchestrationCreate,
    Orchestration,
)

from .auth import (
    Token,
    TokenPayload,
    LoginRequest,
    RegisterRequest,
)


__all__ = [
    # 枚举
    "UserRole",
    "PlatformType",
    "SubscriptionStatus",
    "ExecutionStatus",
    # 通用模型
    "Pricing",
    "Pagination",
    "ErrorDetail",
    "ErrorResponse",
    "ListResponse",
    # 用户模型
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    # 技能模型
    "SkillBase",
    "SkillCreate",
    "SkillUpdate",
    "Skill",
    "SkillSearchResult",
    # 编排模型
    "SkillChainStep",
    "OrchestrationCreate",
    "Orchestration",
    # 认证模型
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
]
