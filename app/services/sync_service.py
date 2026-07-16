"""同步服务 - 真实抓取 + 入库

支持两种模式：
1. run_sync_url_list(db, urls, keyword) - 跑一组 URL（来自知乎站内 URL 列表）
2. run_sync(db, keyword)              - 调知乎开放平台 API
"""
import json
import time
import random
from datetime import datetime
from typing import List, Tuple
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from sqlalchemy.orm import Session

from app.models import Author, Content, SyncLog
from app.services.crawler import upsert_one


def _has_video_hint(text: str) -> bool:
    if not text:
        return False
    return any(k in text for k in ["视频", "实操", "演示", "点击观看", "播放"])


# ========== URL 列表同步（推荐 - 抗风控）==========

def run_sync_url_list(
    db: Session, urls: List[str], keyword: str = "url_list", sleep_s: float = 2.0
) -> SyncLog:
    """抓一组 URL → 入库 → 写 log"""
    log = SyncLog(status="running", keyword=keyword)
    db.add(log)
    db.commit()
    db.refresh(log)

    new_n = updated_n = failed_n = 0
    log.fetched_count = len(urls)
    db.commit()

    try:
        for i, url in enumerate(urls, 1):
            print(f"[{i}/{len(urls)}] {url[:80]}", flush=True)
            try:
                status = upsert_one(db, url)
                if status == "new":
                    new_n += 1
                elif status == "updated":
                    updated_n += 1
                else:
                    failed_n += 1
            except Exception as e:
                failed_n += 1
                db.rollback()
                print(f"  异常: {e}", flush=True)
            time.sleep(sleep_s * random.uniform(0.8, 1.4))

        log.new_count = new_n
        log.updated_count = updated_n
        log.fetched_count = len(urls)  # 这里 fetched_count 等于 URLs 总数
        log.status = "success"
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)[:500]
    finally:
        log.finished_at = datetime.now()
        db.commit()
        db.refresh(log)

    print(f"✅ 同步完成: new={new_n} updated={updated_n} failed={failed_n}", flush=True)
    return log


# ========== 开放平台 API 同步（备用）==========

def run_sync(db: Session, keyword: str = None, page_size: int = 10) -> SyncLog:
    """调知乎开放平台 API 同步"""
    from app.config import settings
    from app.services.zhihu_client import zhihu_client
    from app.schemas.content import ZhihuSearchItem

    keyword = keyword or settings.sync_keyword
    log = SyncLog(status="running", keyword=keyword)
    db.add(log)
    db.commit()
    db.refresh(log)

    try:
        items = zhihu_client.search_all(keyword, max_pages=3, page_size=page_size)
        new_n, updated_n = upsert_items(db, items)
        log.fetched_count = len(items)
        log.new_count = new_n
        log.updated_count = updated_n
        log.status = "success"
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)[:500]
    finally:
        log.finished_at = datetime.now()
        db.commit()
        db.refresh(log)

    return log


def upsert_items(db: Session, items) -> Tuple[int, int]:
    """把知乎 API 返回的 items 写入数据库"""
    new_n = updated_n = 0
    for item in items:
        author_id = f"u_{item.AuthorName or 'unknown'}"
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            author = Author(
                id=author_id,
                name=item.AuthorName or "未知作者",
                avatar=item.AuthorAvatar or None,
                bio=item.AuthorBadgeText or None,
                badge_text=item.AuthorBadgeText or None,
                content_count=1,
                total_votes=item.VoteUpCount or 0,
            )
            db.add(author)
        else:
            author.content_count = (author.content_count or 0) + 1
            author.total_votes = max(author.total_votes or 0, item.VoteUpCount or 0)

        clean_url = item.Url
        if "?" in clean_url:
            try:
                parsed = urlparse(clean_url)
                qs = parse_qs(parsed.query)
                kept = {k: v[0] for k, v in qs.items() if not k.startswith("utm_")}
                clean_url = urlunparse(parsed._replace(query=urlencode(kept) if kept else ""))
            except Exception:
                pass

        text = item.ContentText or ""
        excerpt = (text[:200] + "…") if len(text) > 200 else text

        content = db.query(Content).filter(Content.id == item.ContentID).first()
        if not content:
            content = Content(
                id=item.ContentID,
                type=(item.ContentType or "external").lower(),
                title=item.Title,
                excerpt=excerpt,
                content_text=text,
                source_url=clean_url,
                author_id=author_id,
                author_name=item.AuthorName or "未知作者",
                author_avatar=item.AuthorAvatar or None,
                voteup_count=item.VoteUpCount or 0,
                comment_count=item.CommentCount or 0,
                has_video=_has_video_hint(text),
                edit_time=datetime.now(),
                fetched_via="api",
            )
            db.add(content)
            new_n += 1
        else:
            content.voteup_count = max(content.voteup_count or 0, item.VoteUpCount or 0)
            content.fetched_at = datetime.now()
            updated_n += 1

    db.commit()
    return new_n, updated_n
