"""SQLAlchemy ORM 模型

三张表：
- authors:    作者去重表
- contents:   内容主表（按 id 唯一）
- sync_logs:  同步日志
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from app.db.session import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False, index=True)
    avatar = Column(String(512))
    bio = Column(String(512))
    badge_text = Column(String(256))
    authority_level = Column(String(8), default="0")
    content_count = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    first_seen_at = Column(DateTime, server_default=func.now())
    last_seen_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Content(Base):
    __tablename__ = "contents"

    id = Column(String(64), primary_key=True)
    type = Column(String(16), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    excerpt = Column(Text)
    content_text = Column(Text)
    # === M3 爬虫扩展字段 ===
    raw_html = Column(Text)                # 详情页清洗后的富文本 HTML
    images_json = Column(Text)             # 图片 URL 列表 JSON
    videos_json = Column(Text)             # 视频 URL 列表 JSON
    fetched_via = Column(String(16))       # api / crawler
    crawl_status = Column(String(16))      # pending / ok / failed
    # ======================
    cover = Column(String(512))
    source_url = Column(String(512), nullable=False, index=True)
    author_id = Column(String(64), index=True)
    author_name = Column(String(128), index=True)
    author_avatar = Column(String(512))
    voteup_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    ranking_score = Column(Integer, default=0)
    has_video = Column(Boolean, default=False)
    comment_info = Column(Text)
    edit_time = Column(DateTime, nullable=False, index=True)
    fetched_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_type_edittime", "type", "edit_time"),
        Index("ix_voteup_count", "voteup_count"),
        Index("ix_crawl_status", "crawl_status"),
    )


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime)
    status = Column(String(16))  # running / success / failed
    keyword = Column(String(64))
    fetched_count = Column(Integer, default=0)
    new_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    error_message = Column(Text)
