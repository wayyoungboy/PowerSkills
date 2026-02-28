"""PowerSkills 配置模块"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # SeekDB (唯一的存储基建 - 向量数据库 + 关系型存储)
    seekdb_url: str = Field(
        default="seekdb://localhost:6432",
        description="SeekDB 连接地址"
    )
    seekdb_vector_dimension: int = Field(default=1536, description="向量维度")
    seekdb_index_type: str = Field(default="hnsw", description="向量索引类型")
    seekdb_hnsw_m: int = Field(default=16, description="HNSW M 参数")
    seekdb_hnsw_ef_construction: int = Field(default=200, description="HNSW ef_construction")

    # JWT
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production", description="JWT 密钥"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=15, description="访问令牌过期时间 (分钟)")
    refresh_token_expire_days: int = Field(default=7, description="刷新令牌过期时间 (天)")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 前缀")
    project_name: str = Field(default="PowerSkills", description="项目名称")
    debug: bool = Field(default=False, description="调试模式")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100, description="每分钟请求限制")


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
