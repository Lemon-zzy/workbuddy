"""内容相关路由 - M2 实装（读 DB + 同步接口）"""
import io
import re
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc

from app.db.session import get_db
from app.schemas.content import (
    ContentListItem,
    ContentListResponse,
    ContentDetail,
    StatsResponse,
    AuthorOut,
)
from app.models import Content, Author, SyncLog

router = APIRouter()


def _to_list_item(c: Content) -> ContentListItem:
    return ContentListItem(
        id=c.id,
        type=c.type,
        title=c.title,
        excerpt=c.excerpt or "",
        cover=c.cover,
        source_url=c.source_url,
        author_name=c.author_name or "未知作者",
        author_avatar=c.author_avatar,
        voteup_count=c.voteup_count or 0,
        comment_count=c.comment_count or 0,
        created_at=c.edit_time or c.fetched_at or datetime.now(),
        has_video=c.has_video or False,
        tags=[],
    )


def _to_detail(c: Content, author: Author | None = None) -> ContentDetail:
    import json as _json
    bio = ""
    if author and author.badge_text:
        bio = author.badge_text
    elif c.author_name:
        bio = ""  # 作者没 badge 就留空

    # 解析 images / videos / comments
    try:
        images = _json.loads(c.images_json) if c.images_json else []
    except (ValueError, TypeError):
        images = []
    try:
        videos = _json.loads(c.videos_json) if c.videos_json else []
    except (ValueError, TypeError):
        videos = []
    try:
        comments_raw = _json.loads(c.comment_info) if c.comment_info else []
    except (ValueError, TypeError):
        comments_raw = []
    comments = [
        ContentComment(
            author_name=item.get("author_name", ""),
            content=item.get("content", ""),
            voteup_count=item.get("voteup_count", 0),
            created_at=item.get("created_at", 0),
        )
        for item in comments_raw
    ]

    return ContentDetail(
        id=c.id,
        type=c.type,
        title=c.title,
        excerpt=c.excerpt or "",
        content_html=c.raw_html,  # 富文本 HTML
        cover=c.cover,
        source_url=c.source_url,
        author=AuthorOut(
            id=c.author_id or "u_unknown",
            name=c.author_name or "未知作者",
            avatar=c.author_avatar,
            bio=bio,
            follower_count=0,
        ),
        voteup_count=c.voteup_count or 0,
        comment_count=c.comment_count or 0,
        created_at=c.edit_time or c.fetched_at or datetime.now(),
        fetched_at=c.fetched_at or datetime.now(),
        tags=[],
        has_video=c.has_video or False,
        raw_html=c.raw_html or "",
        images=images,
        videos=videos,
        comments=comments,
    )


@router.get("/{content_id}/md")
async def download_content_md(content_id: str, db: Session = Depends(get_db)):
    """详情页直接生成 md 下载（实时从 DB 生成）"""
    c = db.query(Content).filter(Content.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="内容不存在")

    author_name = ""
    if c.author_id:
        a = db.query(Author).filter(Author.id == c.author_id).first()
        if a:
            author_name = a.name

    md_text = _content_to_md(c, author_name)
    t = c.edit_time or c.fetched_at or datetime.now()
    date_str = t.strftime("%Y-%m-%d") if isinstance(t, datetime) else "unknown"
    slug = _safe_filename(c.title or f"untitled_{c.id}")
    filename = f"{date_str}_{slug}.md"
    # RFC 5987 编码中文 filename
    from urllib.parse import quote
    encoded_filename = quote(filename)

    return StreamingResponse(
        io.BytesIO(md_text.encode("utf-8")),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=\"md.md\"; filename*=UTF-8''{encoded_filename}"
        },
    )


@router.get("", response_model=ContentListResponse)
async def list_contents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    type: Optional[str] = Query(None, description="answer / article / zvideo / external"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    sort: str = Query("newest", description="newest / hot"),
    db: Session = Depends(get_db),
):
    """内容列表"""
    q = db.query(Content)
    if type:
        q = q.filter(Content.type == type)
    if keyword:
        like = f"%{keyword}%"
        q = q.filter(
            or_(
                Content.title.like(like),
                Content.excerpt.like(like),
                Content.author_name.like(like),
            )
        )

    if sort == "hot":
        q = q.order_by(desc(Content.voteup_count), desc(Content.edit_time))
    else:
        q = q.order_by(desc(Content.edit_time), desc(Content.id))

    total = q.count()
    items_db = q.offset((page - 1) * page_size).limit(page_size).all()
    return ContentListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[_to_list_item(c) for c in items_db],
    )


@router.get("/{content_id}", response_model=ContentDetail)
async def get_content(content_id: str, db: Session = Depends(get_db)):
    """内容详情"""
    c = db.query(Content).filter(Content.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="内容不存在")
    author = None
    if c.author_id:
        author = db.query(Author).filter(Author.id == c.author_id).first()
    return _to_detail(c, author)


@router.get("/_stats/summary", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """统计概览"""
    total_contents = db.query(Content).count()
    total_authors = db.query(Author).count()
    total_videos = db.query(Content).filter(Content.has_video == True).count()

    type_rows = (
        db.query(Content.type, func.count(Content.id)).group_by(Content.type).all()
    )
    type_dist = {t: n for t, n in type_rows}

    last_log = db.query(SyncLog).order_by(desc(SyncLog.finished_at)).first()
    last_sync = last_log.finished_at if last_log and last_log.finished_at else None

    return StatsResponse(
        total_contents=total_contents,
        total_authors=total_authors,
        total_videos=total_videos,
        last_sync_at=last_sync,
        type_distribution=type_dist,
    )


@router.post("/_sync/run")
async def trigger_sync(db: Session = Depends(get_db)):
    """手动触发同步"""
    from app.services.sync_service import run_sync
    log = run_sync(db)
    return {
        "id": log.id,
        "status": log.status,
        "fetched": log.fetched_count,
        "new": log.new_count,
        "updated": log.updated_count,
        "error": log.error_message,
        "started_at": log.started_at.isoformat() if log.started_at else None,
        "finished_at": log.finished_at.isoformat() if log.finished_at else None,
    }


@router.get("/_sync/logs")
async def get_sync_logs(limit: int = 10, db: Session = Depends(get_db)):
    """最近同步记录"""
    logs = db.query(SyncLog).order_by(desc(SyncLog.id)).limit(limit).all()
    return {
        "items": [
            {
                "id": l.id,
                "status": l.status,
                "keyword": l.keyword,
                "fetched": l.fetched_count,
                "new": l.new_count,
                "updated": l.updated_count,
                "started_at": l.started_at.isoformat() if l.started_at else None,
                "finished_at": l.finished_at.isoformat() if l.finished_at else None,
                "error": l.error_message,
            }
            for l in logs
        ]
    }


# 末尾占位 - 实际 md 端点已移到文件开头（在 list_contents 之前）
# 但 helper 函数必须保留可被新端点调用
def _safe_filename(s: str, max_len: int = 60) -> str:
    s = re.sub(r'[\\/*?:"<>|]', '', s).strip()
    s = re.sub(r'\s+', '_', s)
    return s[:max_len]


def _content_to_md(c: Content, author_name: str = "") -> str:
    """实时把 Content 渲染成 md 文本（不依赖已导出的文件）"""
    t = c.edit_time or c.fetched_at or datetime.now()
    if isinstance(t, str):
        try:
            t = datetime.fromisoformat(t)
        except (ValueError, TypeError):
            t = datetime.now()

    # raw_html 已是清洗后的干净 HTML；用 html_to_markdown 转换
    from app.services.html_cleaner import clean_zhihu_html
    try:
        import warnings
        from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
        warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
        cleaned_html = clean_zhihu_html(c.raw_html or "")
        soup = BeautifulSoup(cleaned_html, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "")
            if src:
                img.replace_with(BeautifulSoup(f"<span>![{alt}]({src})</span>", "html.parser").span)
        for a in soup.find_all("a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if href and text:
                a.replace_with(BeautifulSoup(f"<span>[{text}]({href})</span>", "html.parser").span)
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            level = int(h.name[1])
            h.replace_with(BeautifulSoup(f"<span>\n\n{'#' * level} {h.get_text(strip=True)}\n\n</span>", "html.parser").span)
        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text:
                p.replace_with(BeautifulSoup(f"<span>\n\n{text}\n\n</span>", "html.parser").span)
        for li in soup.find_all("li"):
            text = li.get_text().strip()
            li.replace_with(BeautifulSoup(f"<span>\n- {text}</span>", "html.parser").span)
        for bq in soup.find_all("blockquote"):
            text = bq.get_text().strip()
            md = "\n\n" + "\n".join(f"> {line}" for line in text.splitlines()) + "\n\n"
            bq.replace_with(BeautifulSoup(f"<span>{md}</span>", "html.parser").span)
        body_md = soup.get_text(separator="\n")
        body_md = re.sub(r'\n{3,}', '\n\n', body_md).strip()
    except Exception as e:
        body_md = f"_(渲染失败: {e})_\n\n{c.content_text or ''}"

    type_map = {"answer": "回答", "article": "文章", "zvideo": "视频", "question": "问题"}
    type_zh = type_map.get(c.type, c.type or "unknown")
    author = author_name or c.author_name or "未知作者"

    md = f"""---
id: {c.id}
type: {c.type}
type_zh: {type_zh}
title: "{c.title}"
author: "{author}"
source_url: {c.source_url}
voteup_count: {c.voteup_count or 0}
comment_count: {c.comment_count or 0}
has_video: {c.has_video or False}
created_at: {t.isoformat()}
exported_at: {datetime.now().isoformat()}
---

# {c.title}

> {type_zh} · **{author}**
> 发布于 {t.strftime('%Y-%m-%d %H:%M')}
> 赞同 {c.voteup_count or 0} · 评论 {c.comment_count or 0}

## 摘要

{c.excerpt or '(无摘要)'}

## 正文

{body_md if body_md else '_(本篇目暂无正文)_'}

## 引用

```
{author} ({t.strftime('%Y-%m-%d')}). {c.title}. workbuddy 专题 · 知乎内容聚合.
原文链接: {c.source_url}
```

## 原文

[{c.source_url}]({c.source_url})

---

*本文件由 workbuddy 专题 API 实时生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return md


@router.get("/{content_id}/md")
async def download_content_md(content_id: str, db: Session = Depends(get_db)):
    """详情页直接生成 md 下载（实时从 DB 生成）"""
    c = db.query(Content).filter(Content.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="内容不存在")

    author_name = ""
    if c.author_id:
        a = db.query(Author).filter(Author.id == c.author_id).first()
        if a:
            author_name = a.name

    md_text = _content_to_md(c, author_name)
    t = c.edit_time or c.fetched_at or datetime.now()
    date_str = t.strftime("%Y-%m-%d") if isinstance(t, datetime) else "unknown"
    slug = _safe_filename(c.title or f"untitled_{c.id}")
    filename = f"{date_str}_{slug}.md"

    return StreamingResponse(
        io.BytesIO(md_text.encode("utf-8")),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
