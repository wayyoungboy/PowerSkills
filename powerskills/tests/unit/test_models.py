"""技能模型单元测试"""

import pytest

from powerskills.core.models import (
    Skill,
    SkillCreate,
    PlatformType,
    Pricing,
    SkillSearchResult,
    Pagination,
    ListResponse,
)


class TestSkillModels:
    """技能模型测试"""

    def test_skill_creation(self):
        """测试技能创建"""
        skill = Skill(
            skill_id="sk_test123",
            skill_name="Test Skill",
            platform=PlatformType.COZE,
            description="A test skill",
            developer="test_user",
            capabilities=["coding", "testing"],
            tags=["test", "demo"],
            pricing=Pricing(type="free"),
        )

        assert skill.skill_id == "sk_test123"
        assert skill.skill_name == "Test Skill"
        assert skill.platform == PlatformType.COZE
        assert skill.rating == 0.0
        assert skill.usage_count == 0

    def test_skill_create_from_dict(self):
        """测试从字典创建技能"""
        skill_data = SkillCreate(
            skill_name="New Skill",
            platform=PlatformType.DIFY,
            description="A new skill",
            capabilities=["analysis"],
        )

        assert skill_data.skill_name == "New Skill"
        assert skill_data.platform == PlatformType.DIFY

    def test_pricing_model(self):
        """测试定价模型"""
        pricing = Pricing(type="subscription", price=9.99, currency="USD")

        assert pricing.type == "subscription"
        assert pricing.price == 9.99
        assert pricing.currency == "USD"

    def test_pagination_model(self):
        """测试分页模型"""
        pagination = Pagination(page=1, limit=20, total=100, total_pages=5)

        assert pagination.page == 1
        assert pagination.limit == 20
        assert pagination.total == 100
        assert pagination.total_pages == 5

    def test_list_response_model(self):
        """测试列表响应模型"""
        response = ListResponse(
            data=[{"id": 1}, {"id": 2}],
            pagination=Pagination(page=1, limit=20, total=2, total_pages=1),
        )

        assert len(response.data) == 2
        assert response.pagination.total == 2


class TestPlatformType:
    """平台类型枚举测试"""

    def test_platform_types(self):
        """测试平台类型枚举值"""
        assert PlatformType.COZE.value == "coze"
        assert PlatformType.DIFY.value == "dify"
        assert PlatformType.LANGCHAIN.value == "langchain"
        assert PlatformType.CURSOR.value == "cursor"
        assert PlatformType.GITHUB.value == "github"
        assert PlatformType.CUSTOM.value == "custom"
