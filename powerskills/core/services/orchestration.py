"""编排服务"""

import asyncio
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from powerskills.core.models.orchestration import Orchestration, OrchestrationCreate, SkillChainStep
from powerskills.core.models.common import PlatformType
from powerskills.db.seekdb import seekdb_client


class OrchestrationService:
    """编排服务"""

    async def create_plan(self, user_id: str, task_data: OrchestrationCreate) -> Orchestration:
        """创建编排计划"""
        plan_id = f"op_{uuid4().hex[:12]}"
        now = datetime.utcnow()

        # AI 生成技能链（简化版，实际应调用 AI 服务）
        skill_chain = await self._generate_skill_chain(task_data.task_description)

        plan_dict = {
            "plan_id": plan_id,
            "user_id": user_id,
            "task_description": task_data.task_description,
            "skill_chain": [step.model_dump() for step in skill_chain],
            "status": "pending_confirmation",
            "estimated_duration": len(skill_chain) * 30,  # 估算每个步骤 30 秒
            "created_at": now,
            "executed_at": None,
        }

        await seekdb_client.insert("orchestration_plans", plan_dict)

        return Orchestration(
            plan_id=plan_id,
            task_description=task_data.task_description,
            skill_chain=skill_chain,
            status="pending_confirmation",
            estimated_duration=len(skill_chain) * 30,
            created_at=now,
        )

    async def get_plan(self, plan_id: str) -> Optional[Orchestration]:
        """获取编排计划"""
        plan_data = await seekdb_client.get("orchestration_plans", plan_id)
        if not plan_data:
            return None

        return self._parse_plan(plan_data)

    async def execute_plan(self, plan_id: str) -> Orchestration:
        """执行编排计划"""
        plan = await self.get_plan(plan_id)
        if not plan:
            raise ValueError("编排计划不存在")

        if plan.status == "running":
            raise ValueError("编排计划已在执行中")

        # 更新状态为运行中
        await seekdb_client.update(
            "orchestration_plans", plan_id, {"status": "running", "executed_at": datetime.utcnow()}
        )

        # 异步执行技能链
        asyncio.create_task(self._execute_skill_chain(plan_id, plan.skill_chain))

        plan.status = "running"
        plan.executed_at = datetime.utcnow()

        return plan

    async def cancel_plan(self, plan_id: str) -> bool:
        """取消编排计划"""
        plan = await self.get_plan(plan_id)
        if not plan:
            return False

        if plan.status in ["completed", "failed"]:
            return False

        await seekdb_client.update("orchestration_plans", plan_id, {"status": "cancelled"})

        return True

    async def list_plans(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> tuple[List[Orchestration], dict]:
        """获取用户编排计划列表"""
        offset = (page - 1) * limit

        plans_data = await seekdb_client.query(
            "orchestration_plans", filters={"user_id": user_id}, limit=limit, offset=offset
        )

        plans = [self._parse_plan(p) for p in plans_data]

        return plans, {"page": page, "limit": limit}

    async def _generate_skill_chain(self, task_description: str) -> List[SkillChainStep]:
        """生成技能链（简化版 AI 生成）"""
        # 实际生产环境应调用 AI 服务进行分析和技能匹配
        # 这里返回示例技能链

        task_lower = task_description.lower()

        chain = []
        step_num = 1

        # 网页抓取步骤
        if (
            "网站" in task_lower
            or "网页" in task_lower
            or "url" in task_lower
            or "http" in task_lower
        ):
            chain.append(
                SkillChainStep(
                    step=step_num,
                    skill_id="sk_web_scraper",
                    skill_name="Web Scraper Pro",
                    platform=PlatformType.COZE,
                    input={"url": "input_url"},
                    output_format="JSON",
                )
            )
            step_num += 1

        # 内容分析步骤
        if "分析" in task_lower or "分析报告" in task_lower:
            chain.append(
                SkillChainStep(
                    step=step_num,
                    skill_id="sk_content_analyzer",
                    skill_name="Content Analyzer",
                    platform=PlatformType.DIFY,
                    input_format="JSON",
                    output_format="JSON",
                    depends_on=[step_num - 1] if step_num > 1 else [],
                )
            )
            step_num += 1

        # 报告生成步骤
        if "报告" in task_lower or "生成" in task_lower:
            chain.append(
                SkillChainStep(
                    step=step_num,
                    skill_id="sk_report_generator",
                    skill_name="Report Generator",
                    platform=PlatformType.LANGCHAIN,
                    input_format="JSON",
                    output_format="PDF",
                    depends_on=[step_num - 1] if step_num > 1 else [],
                )
            )

        # 默认至少返回一个技能
        if not chain:
            chain.append(
                SkillChainStep(
                    step=1,
                    skill_id="sk_default",
                    skill_name="Default Skill",
                    platform=PlatformType.CUSTOM,
                    output_format="JSON",
                )
            )

        return chain

    async def _execute_skill_chain(self, plan_id: str, skill_chain: List[SkillChainStep]):
        """执行技能链"""
        try:
            # 模拟执行每个步骤
            for step in skill_chain:
                # 实际应调用对应平台的适配器执行技能
                await asyncio.sleep(1)  # 模拟执行时间

            # 执行完成
            await seekdb_client.update("orchestration_plans", plan_id, {"status": "completed"})
        except Exception as e:
            # 执行失败
            await seekdb_client.update(
                "orchestration_plans", plan_id, {"status": "failed", "error": str(e)}
            )

    def _parse_plan(self, data: dict) -> Orchestration:
        """解析编排计划数据"""
        skill_chain = []
        if data.get("skill_chain"):
            for step_data in data["skill_chain"]:
                skill_chain.append(SkillChainStep(**step_data))

        return Orchestration(
            plan_id=data["plan_id"],
            task_description=data["task_description"],
            skill_chain=skill_chain,
            status=data.get("status", "pending_confirmation"),
            estimated_duration=data.get("estimated_duration", 0),
            created_at=data.get("created_at", datetime.utcnow()),
            executed_at=data.get("executed_at"),
        )


orchestration_service = OrchestrationService()
