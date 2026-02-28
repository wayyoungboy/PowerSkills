"""技能模型"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from .common import PlatformType, Pricing


class SkillBase(BaseModel):
    """技能基础模型"""

    skill_name: str
    description: Optional[str] = None
    platform: PlatformType
    developer: Optional[str] = None
    capabilities: List[str] = []
    tags: List[str] = []
    pricing: Pricing = Pricing()


class SkillCreate(SkillBase):
    """技能创建请求"""

    pass


class SkillUpdate(BaseModel):
    """技能更新请求"""

    skill_name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    pricing: Optional[Pricing] = None


class Skill(SkillBase):
    """技能响应模型"""

    skill_id: str = Field(default_factory=lambda: f"sk_{__import__('uuid').uuid4().hex[:12]}")
    rating: float = 0.0
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class SkillSearchResult(Skill):
    """技能搜索结果"""

    similarity: Optional[float] = None
