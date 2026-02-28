"""PowerSkills 主应用"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from powerskills.core.config import settings
from powerskills.db.seekdb import seekdb_client
from powerskills.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    try:
        seekdb_client.connect()
        await seekdb_client.create_tables()
    except Exception as e:
        print(f"SeekDB 连接失败：{e}")

    yield

    # 关闭时
    seekdb_client.close()


app = FastAPI(
    title=settings.project_name,
    description="AI 技能统一编排引擎 API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.project_name}


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Welcome to PowerSkills API", "docs": "/docs", "version": "0.1.0"}
