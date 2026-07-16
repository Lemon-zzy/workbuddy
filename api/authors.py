"""作者相关路由 - 真实数据库"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models import Author, Content

router = APIRouter()


@router.get("")
async def list_authors(sort: str = "content", limit: int = 50):
    """作者聚合列表
    - sort=content  按发布数排序
    - sort=votes    按总赞同数排序
    """
    db = SessionLocal()
    try:
        authors = db.query(Author).all()
        items = []
        for a in authors:
            items.append({
                "id": a.id,
                "name": a.name,
                "avatar": a.avatar,
                "bio": a.bio,
                "badge_text": a.badge_text,
                "follower_count": getattr(a, 'follower_count', 0) or 0,
                "content_count": a.content_count or 0,
                "total_votes": a.total_votes or 0,
            })

        if sort == "votes":
            items.sort(key=lambda x: x["total_votes"], reverse=True)
        else:
            items.sort(key=lambda x: x["content_count"], reverse=True)

        return {
            "total": len(items),
            "items": items[:limit],
        }
    finally:
        db.close()


@router.get("/{author_id}")
async def author_detail(author_id: str):
    """作者详情 + 作品列表"""
    db = SessionLocal()
    try:
        a = db.query(Author).filter(Author.id == author_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="作者不存在")

        works = db.query(Content).filter(Content.author_id == author_id).order_by(
            Content.voteup_count.desc().nullslast()
        ).limit(50).all()

        return {
            "id": a.id,
            "name": a.name,
            "avatar": a.avatar,
            "bio": a.bio,
            "badge_text": a.badge_text,
            "follower_count": getattr(a, 'follower_count', 0) or 0,
            "content_count": a.content_count or 0,
            "total_votes": a.total_votes or 0,
            "works": [
                {
                    "id": w.id,
                    "title": w.title,
                    "excerpt": w.excerpt or "",
                    "type": w.type,
                    "voteup_count": w.voteup_count or 0,
                    "comment_count": w.comment_count or 0,
                    "source_url": w.source_url,
                    "created_at": (w.edit_time or w.fetched_at or w.created_at).isoformat() if (w.edit_time or w.fetched_at or w.created_at) else None,
                    "has_video": bool(w.has_video),
                }
                for w in works
            ],
        }
    finally:
        db.close()
