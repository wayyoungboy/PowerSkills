"""SeekDB 数据库连接模块"""

from typing import Optional, Any, Dict, List
import pyseekdb as seekdb

from powerskills.core.config import settings


class SeekDBClient:
    """SeekDB 客户端"""

    _instance: Optional["SeekDBClient"] = None
    _client: Optional[Any] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Any:
        """连接 SeekDB"""
        if self._client is None:
            self._client = seekdb.connect(
                url=settings.seekdb_url,
                vector_dimension=settings.seekdb_vector_dimension,
            )
        return self._client

    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None

    async def create_tables(self):
        """创建表结构"""
        client = self.connect()

        await client.create_table(
            "skills",
            {
                "skill_id": "string",
                "skill_name": "string",
                "platform": "string",
                "developer": "string",
                "description": "string",
                "capabilities": "json",
                "rating": "float",
                "usage_count": "int",
                "pricing": "json",
                "tags": "json",
                "created_at": "timestamp",
                "updated_at": "timestamp",
            },
            primary_key="skill_id",
        )

        await client.create_table(
            "skill_vectors",
            {
                "skill_id": "string",
                "skill_vector": "vector",
                "capability_vectors": "json",
            },
            primary_key="skill_id",
        )

        await client.create_table(
            "users",
            {
                "user_id": "string",
                "email": "string",
                "password_hash": "string",
                "name": "string",
                "avatar_url": "string",
                "role": "string",
                "created_at": "timestamp",
            },
            primary_key="user_id",
        )

        await client.create_table(
            "orchestration_plans",
            {
                "plan_id": "string",
                "user_id": "string",
                "task_description": "string",
                "skill_chain": "json",
                "status": "string",
                "created_at": "timestamp",
                "executed_at": "timestamp",
            },
            primary_key="plan_id",
        )

        await client.create_table(
            "task_vectors",
            {
                "task_id": "string",
                "task_description": "string",
                "task_vector": "vector",
                "required_capabilities": "json",
            },
            primary_key="task_id",
        )

        await client.create_vector_index(
            "skill_vectors",
            "idx_skill_vector",
            index_type=settings.seekdb_index_type,
            m=settings.seekdb_hnsw_m,
            ef_construction=settings.seekdb_hnsw_ef_construction,
        )

        await client.create_vector_index(
            "task_vectors",
            "idx_task_vector",
            index_type=settings.seekdb_index_type,
            m=settings.seekdb_hnsw_m,
            ef_construction=settings.seekdb_hnsw_ef_construction,
        )

    async def vector_search(
        self,
        table: str,
        vector_column: str,
        query_vector: list,
        top_k: int = 10,
        filter_conditions: Optional[dict] = None,
    ) -> list:
        """向量搜索"""
        client = self.connect()
        return await client.vector_search(
            table=table,
            vector_column=vector_column,
            query_vector=query_vector,
            top_k=top_k,
            filter_conditions=filter_conditions,
        )

    async def insert(self, table: str, data: dict):
        """插入数据"""
        client = self.connect()
        await client.insert(table, data)

    async def update(self, table: str, primary_key: str, data: dict):
        """更新数据"""
        client = self.connect()
        await client.update(table, primary_key, data)

    async def delete(self, table: str, primary_key: str):
        """删除数据"""
        client = self.connect()
        await client.delete(table, primary_key)

    async def get(self, table: str, primary_key: str) -> Optional[dict]:
        """获取单条数据"""
        client = self.connect()
        return await client.get(table, primary_key)

    async def query(
        self, table: str, filters: Optional[dict] = None, limit: int = 100, offset: int = 0
    ) -> list:
        """查询数据"""
        client = self.connect()
        return await client.query(table, filters=filters, limit=limit, offset=offset)


seekdb_client = SeekDBClient()
