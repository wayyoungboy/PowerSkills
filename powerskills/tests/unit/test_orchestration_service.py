"""编排服务单元测试"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from powerskills.core.services.orchestration import OrchestrationService
from powerskills.core.models import OrchestrationCreate, PlatformType, SkillChainStep


class TestOrchestrationService:
    """编排服务测试"""

    @pytest.mark.asyncio
    async def test_create_plan(self):
        """测试创建编排计划"""
        service = OrchestrationService()

        task_data = OrchestrationCreate(
            task_description="分析网站并生成报告",
            options={"max_steps": 5}
        )

        with patch.object(service, '_generate_skill_chain') as mock_generate:
            mock_generate.return_value = [
                SkillChainStep(
                    step=1,
                    skill_id="sk_test",
                    skill_name="Test Skill",
                    platform=PlatformType.COZE,
                )
            ]

            with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
                mock_db.insert = AsyncMock()

                plan = await service.create_plan("usr_test", task_data)

                assert plan is not None
                assert plan.status == "pending_confirmation"
                assert len(plan.skill_chain) == 1
                mock_db.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_plan(self):
        """测试获取编排计划"""
        service = OrchestrationService()

        mock_plan_data = {
            "plan_id": "op_test123",
            "task_description": "Test task",
            "skill_chain": [
                {
                    "step": 1,
                    "skill_id": "sk_1",
                    "skill_name": "Skill 1",
                    "platform": "coze",
                    "input": {},
                    "output_format": "JSON",
                    "depends_on": [],
                }
            ],
            "status": "pending_confirmation",
            "estimated_duration": 30,
            "created_at": datetime.utcnow(),
            "executed_at": None,
        }

        with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
            mock_db.get = AsyncMock(return_value=mock_plan_data)

            plan = await service.get_plan("op_test123")

            assert plan is not None
            assert plan.plan_id == "op_test123"
            assert len(plan.skill_chain) == 1

    @pytest.mark.asyncio
    async def test_get_plan_not_found(self):
        """测试获取不存在的编排计划"""
        service = OrchestrationService()

        with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
            mock_db.get = AsyncMock(return_value=None)

            plan = await service.get_plan("op_nonexistent")

            assert plan is None

    @pytest.mark.asyncio
    async def test_execute_plan(self):
        """测试执行编排计划"""
        service = OrchestrationService()

        mock_plan = MagicMock(
            plan_id="op_test",
            status="pending_confirmation",
            skill_chain=[MagicMock()],
            executed_at=None,
        )

        with patch.object(service, 'get_plan') as mock_get:
            mock_get.return_value = mock_plan

            with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
                mock_db.update = AsyncMock()

                with patch('asyncio.create_task'):
                    plan = await service.execute_plan("op_test")

                    assert plan.status == "running"
                    mock_db.update.assert_called()

    @pytest.mark.asyncio
    async def test_execute_plan_not_found(self):
        """测试执行不存在的计划"""
        service = OrchestrationService()

        with patch.object(service, 'get_plan') as mock_get:
            mock_get.return_value = None

            with pytest.raises(ValueError, match="编排计划不存在"):
                await service.execute_plan("op_nonexistent")

    @pytest.mark.asyncio
    async def test_execute_plan_already_running(self):
        """测试执行已在运行的计划"""
        service = OrchestrationService()

        mock_plan = MagicMock(plan_id="op_test", status="running")

        with patch.object(service, 'get_plan') as mock_get:
            mock_get.return_value = mock_plan

            with pytest.raises(ValueError, match="编排计划已在执行中"):
                await service.execute_plan("op_test")

    @pytest.mark.asyncio
    async def test_cancel_plan(self):
        """测试取消编排计划"""
        service = OrchestrationService()

        mock_plan = MagicMock(plan_id="op_test", status="pending_confirmation")

        with patch.object(service, 'get_plan') as mock_get:
            mock_get.return_value = mock_plan

            with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
                mock_db.update = AsyncMock()

                result = await service.cancel_plan("op_test")

                assert result is True
                mock_db.update.assert_called_once_with(
                    "orchestration_plans", "op_test", {"status": "cancelled"}
                )

    @pytest.mark.asyncio
    async def test_cancel_completed_plan(self):
        """测试取消已完成的计划"""
        service = OrchestrationService()

        mock_plan = MagicMock(plan_id="op_test", status="completed")

        with patch.object(service, 'get_plan') as mock_get:
            mock_get.return_value = mock_plan

            result = await service.cancel_plan("op_test")

            assert result is False

    @pytest.mark.asyncio
    async def test_list_plans(self):
        """测试获取编排计划列表"""
        service = OrchestrationService()

        mock_plans = [
            {
                "plan_id": "op_1",
                "task_description": "Task 1",
                "skill_chain": [],
                "status": "completed",
                "created_at": datetime.utcnow(),
                "executed_at": None,
            },
            {
                "plan_id": "op_2",
                "task_description": "Task 2",
                "skill_chain": [],
                "status": "pending_confirmation",
                "created_at": datetime.utcnow(),
                "executed_at": None,
            },
        ]

        with patch('powerskills.core.services.orchestration.seekdb_client') as mock_db:
            mock_db.query = AsyncMock(return_value=mock_plans)

            plans, pagination = await service.list_plans("usr_test", page=1, limit=20)

            assert len(plans) == 2
            assert pagination["page"] == 1
            assert pagination["limit"] == 20

    @pytest.mark.asyncio
    async def test_generate_skill_chain_with_web_scraping(self):
        """测试生成技能链 - 网页抓取"""
        service = OrchestrationService()

        chain = await service._generate_skill_chain("分析 https://example.com 网站")

        assert len(chain) >= 1
        assert any("Web Scraper" in step.skill_name for step in chain)

    @pytest.mark.asyncio
    async def test_generate_skill_chain_with_analysis(self):
        """测试生成技能链 - 内容分析"""
        service = OrchestrationService()

        chain = await service._generate_skill_chain("分析报告数据")

        assert len(chain) >= 1
        assert any("Analyzer" in step.skill_name for step in chain)

    @pytest.mark.asyncio
    async def test_generate_skill_chain_with_report(self):
        """测试生成技能链 - 报告生成"""
        service = OrchestrationService()

        chain = await service._generate_skill_chain("生成竞品分析报告")

        assert len(chain) >= 1
        assert any("Report" in step.skill_name for step in chain)

    @pytest.mark.asyncio
    async def test_generate_skill_chain_default(self):
        """测试生成技能链 - 默认情况"""
        service = OrchestrationService()

        chain = await service._generate_skill_chain("随便一个任务描述 xyz123")

        assert len(chain) >= 1
        assert chain[0].skill_id == "sk_default"
