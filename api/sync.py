"""手动触发同步"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import SessionLocal
from app.services.sync_service import run_sync_url_list, run_sync
from app.models import SyncLog

router = APIRouter()


class SyncUrlListRequest(BaseModel):
    urls: List[str]
    keyword: Optional[str] = "manual"
    sleep_s: float = 2.0


class SyncResponse(BaseModel):
    log_id: int
    status: str
    fetched_count: int
    new_count: int
    updated_count: int
    error_message: Optional[str] = None
    started_at: str
    finished_at: Optional[str] = None


def _to_resp(log: SyncLog) -> SyncResponse:
    return SyncResponse(
        log_id=log.id,
        status=log.status,
        fetched_count=log.fetched_count or 0,
        new_count=log.new_count or 0,
        updated_count=log.updated_count or 0,
        error_message=log.error_message,
        started_at=log.started_at.isoformat() if log.started_at else "",
        finished_at=log.finished_at.isoformat() if log.finished_at else None,
    )


@router.post("/run_url_list", response_model=SyncResponse)
async def sync_url_list(req: SyncUrlListRequest):
    """手动同步一组 URL（推荐 - 来自浏览器控制台提取的 URL 列表）"""
    db = SessionLocal()
    try:
        log = run_sync_url_list(db, req.urls, req.keyword, req.sleep_s)
        return _to_resp(log)
    finally:
        db.close()


@router.post("/run", response_model=SyncResponse)
async def sync_api(keyword: Optional[str] = None, page_size: int = 10):
    """调知乎开放平台 API 同步（备用）"""
    db = SessionLocal()
    try:
        log = run_sync(db, keyword=keyword, page_size=page_size)
        return _to_resp(log)
    finally:
        db.close()


@router.get("/logs")
async def list_logs(limit: int = 20):
    """最近的同步日志"""
    db = SessionLocal()
    try:
        rows = db.query(SyncLog).order_by(SyncLog.id.desc()).limit(limit).all()
        return {
            "total": len(rows),
            "items": [
                {
                    "id": r.id,
                    "status": r.status,
                    "keyword": r.keyword,
                    "fetched_count": r.fetched_count,
                    "new_count": r.new_count,
                    "updated_count": r.updated_count,
                    "error_message": r.error_message,
                    "started_at": r.started_at.isoformat() if r.started_at else None,
                    "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                }
                for r in rows
            ],
        }
    finally:
        db.close()
