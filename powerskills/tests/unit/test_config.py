"""配置模块单元测试"""

import pytest
from unittest.mock import patch, MagicMock

from powerskills.core.config import Settings


class TestSettings:
    """配置测试"""

    def test_default_settings(self):
        """测试默认配置"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()

            assert settings.project_name == "PowerSkills"
            assert settings.api_v1_prefix == "/api/v1"
            assert settings.debug is False

    def test_jwt_settings(self):
        """测试 JWT 配置"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()

            assert settings.jwt_algorithm == "HS256"
            assert settings.access_token_expire_minutes == 15
            assert settings.refresh_token_expire_days == 7

    def test_seekdb_settings(self):
        """测试 SeekDB 配置"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()

            assert settings.seekdb_url == "seekdb://localhost:6432"
            assert settings.seekdb_vector_dimension == 1536
            assert settings.seekdb_index_type == "hnsw"
            assert settings.seekdb_hnsw_m == 16

    def test_rate_limit_settings(self):
        """测试限流配置"""
        with patch.dict("os.environ", {}, clear=True):
            settings = Settings()

            assert settings.rate_limit_per_minute == 100

    def test_settings_from_env(self):
        """测试从环境变量加载配置"""
        with patch.dict(
            "os.environ",
            {"PROJECT_NAME": "TestApp", "DEBUG": "true", "RATE_LIMIT_PER_MINUTE": "200"},
            clear=True,
        ):
            settings = Settings()

            assert settings.project_name == "TestApp"
            assert settings.debug is True
            assert settings.rate_limit_per_minute == 200


class TestGetSettings:
    """配置单例测试"""

    def test_get_settings_returns_same_instance(self):
        """测试获取配置返回相同实例"""
        from powerskills.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2
