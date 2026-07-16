"""workbuddy 专题 - 后端 FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.contents import router as contents_router
from app.api.authors import router as authors_router
from app.api.stats import router as stats_router
from app.api.sync import router as sync_router
from app.api.md import router as md_router
from app.db.session import init_db
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库"""
    init_db()
    yield


app = FastAPI(
    title="workbuddy 专题 API",
    description="知乎 workbuddy 相关内容聚合知识库",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contents_router, prefix="/api/contents", tags=["内容"])
app.include_router(authors_router, prefix="/api/authors", tags=["作者"])
app.include_router(stats_router, prefix="/api/stats", tags=["统计"])
app.include_router(sync_router, prefix="/api/_sync", tags=["同步"])
app.include_router(md_router, prefix="/api/md", tags=["md文件库"])


@app.get("/")
async def root():
    return {
        "project": "workbuddy 专题",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
    )
