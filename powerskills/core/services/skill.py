"""技能服务"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from powerskills.core.models.skill import (
    Skill,
    SkillCreate,
    SkillUpdate,
    SkillSearchResult,
    Pricing,
)
from powerskills.core.models.common import PlatformType, Pagination
from powerskills.db.seekdb import seekdb_client


class SkillService:
    """技能服务"""

    async def create_skill(self, skill_data: SkillCreate, developer_id: str) -> Skill:
        """创建技能"""
        skill_id = f"sk_{uuid4().hex[:12]}"
        now = datetime.utcnow()

        skill_dict = {
            "skill_id": skill_id,
            "skill_name": skill_data.skill_name,
            "platform": skill_data.platform.value,
            "developer": developer_id,
            "description": skill_data.description,
            "capabilities": skill_data.capabilities,
            "tags": skill_data.tags,
            "pricing": skill_data.pricing.model_dump(),
            "rating": 0.0,
            "usage_count": 0,
            "created_at": now,
            "updated_at": now,
        }

        await seekdb_client.insert("skills", skill_dict)

        return Skill(
            skill_id=skill_id,
            skill_name=skill_data.skill_name,
            platform=skill_data.platform,
            developer=developer_id,
            description=skill_data.description,
            capabilities=skill_data.capabilities,
            tags=skill_data.tags,
            pricing=skill_data.pricing,
            created_at=now,
            updated_at=now,
        )

    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        """获取技能详情"""
        skill_data = await seekdb_client.get("skills", skill_id)
        if not skill_data:
            return None

        return self._parse_skill(skill_data)

    async def update_skill(self, skill_id: str, skill_data: SkillUpdate) -> Optional[Skill]:
        """更新技能"""
        existing = await seekdb_client.get("skills", skill_id)
        if not existing:
            return None

        update_dict = skill_data.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()

        if "platform" in update_dict and update_dict["platform"]:
            update_dict["platform"] = update_dict["platform"].value
        if "pricing" in update_dict and update_dict["pricing"]:
            update_dict["pricing"] = update_dict["pricing"].model_dump()

        await seekdb_client.update("skills", skill_id, update_dict)

        return await self.get_skill(skill_id)

    async def delete_skill(self, skill_id: str) -> bool:
        """删除技能"""
        existing = await seekdb_client.get("skills", skill_id)
        if not existing:
            return False

        await seekdb_client.delete("skills", skill_id)
        return True

    async def list_skills(
        self, platform: Optional[PlatformType] = None, page: int = 1, limit: int = 20
    ) -> tuple[List[Skill], Pagination]:
        """获取技能列表"""
        filters = {}
        if platform:
            filters["platform"] = platform.value

        offset = (page - 1) * limit
        skills_data = await seekdb_client.query(
            "skills", filters=filters, limit=limit, offset=offset
        )

        # 获取总数
        all_skills = await seekdb_client.query("skills", filters=filters, limit=10000)
        total = len(all_skills)

        skills = [self._parse_skill(s) for s in skills_data]

        pagination = Pagination(
            page=page,
            limit=limit,
            total=total,
            total_pages=(total + limit - 1) // limit if limit > 0 else 0,
        )

        return skills, pagination

    async def search_skills(
        self,
        query: str,
        platforms: Optional[List[PlatformType]] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[SkillSearchResult]:
        """搜索技能"""
        filters = {}
        if platforms:
            filters["platform"] = [p.value for p in platforms]

        # 简单关键词匹配（生产环境应使用向量检索）
        skills_data = await seekdb_client.query("skills", filters=filters, limit=limit * 2)

        results = []
        query_lower = query.lower()

        for skill in skills_data:
            if (
                query_lower in skill.get("skill_name", "").lower()
                or query_lower in skill.get("description", "").lower()
            ):
                parsed = self._parse_skill(skill)
                results.append(SkillSearchResult(**parsed.model_dump(), similarity=0.9))

            if len(results) >= limit:
                break

        return results

    async def increment_usage(self, skill_id: str):
        """增加技能使用次数"""
        skill_data = await seekdb_client.get("skills", skill_id)
        if skill_data:
            new_count = skill_data.get("usage_count", 0) + 1
            await seekdb_client.update("skills", skill_id, {"usage_count": new_count})

    def _parse_skill(self, data: dict) -> Skill:
        """解析技能数据"""
        return Skill(
            skill_id=data["skill_id"],
            skill_name=data["skill_name"],
            platform=PlatformType(data.get("platform", "custom")),
            developer=data.get("developer"),
            description=data.get("description"),
            capabilities=data.get("capabilities", []),
            tags=data.get("tags", []),
            pricing=data.get("pricing", {}),
            rating=data.get("rating", 0.0),
            usage_count=data.get("usage_count", 0),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )


skill_service = SkillService()
