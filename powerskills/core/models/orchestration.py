"""编排模型"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from .common import PlatformType


class SkillChainStep(BaseModel):
    """技能链步骤"""

    step: int
    skill_id: str
    skill_name: str
    platform: PlatformType
    input: Dict[str, Any] = {}
    output_format: str = "JSON"
    depends_on: List[int] = []


class OrchestrationCreate(BaseModel):
    """编排创建请求"""

    task_description: str
    options: Dict[str, Any] = Field(default_factory=dict)


class Orchestration(BaseModel):
    """编排响应模型"""

    plan_id: str = Field(default_factory=lambda: f"op_{__import__('uuid').uuid4().hex[:12]}")
    task_description: str
    skill_chain: List[SkillChainStep] = []
    status: str = (
        "pending_confirmation"  # pending_confirmation, pending, running, completed, failed
    )
    estimated_duration: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
