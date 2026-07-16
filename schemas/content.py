"""Pydantic 数据模型

前端可见的 schema (ContentListItem / ContentDetail) - 保持稳定
知乎 API 真实响应 schema (ZhihuSearchItem / ZhihuSearchResponse) - 适配真实字段
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== 前端 API schema（保持稳定）==========

class AuthorOut(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    follower_count: int = 0


class VideoOut(BaseModel):
    id: str
    title: str
    cover: Optional[str] = None
    duration: Optional[int] = None
    play_url: Optional[str] = None
    embeddable: bool = False


class ContentBase(BaseModel):
    id: str
    type: str = Field(..., description="answer / article / zvideo / external")
    title: str
    excerpt: str = ""
    content_html: Optional[str] = None
    cover: Optional[str] = None
    source_url: str
    author: AuthorOut
    voteup_count: int = 0
    comment_count: int = 0
    created_at: datetime
    fetched_at: datetime
    tags: List[str] = []
    has_video: bool = False


class ContentListItem(BaseModel):
    """列表页 - 简化字段"""
    id: str
    type: str
    title: str
    excerpt: str
    cover: Optional[str] = None
    source_url: str
    author_name: str
    author_avatar: Optional[str] = None
    voteup_count: int = 0
    comment_count: int = 0
    created_at: datetime
    has_video: bool = False
    tags: List[str] = []


class ContentDetail(ContentBase):
    """详情页 - 完整字段"""
    pass


class ContentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ContentListItem]


class StatsResponse(BaseModel):
    total_contents: int
    total_authors: int
    total_videos: int
    last_sync_at: Optional[datetime] = None
    type_distribution: dict = {}


# ========== 知乎 API 真实响应 schema ==========

class ZhihuCommentInfo(BaseModel):
    Content: str


class ZhihuSearchItem(BaseModel):
    """知乎开放平台 search 接口的单个 item"""
    Title: str
    ContentType: str = ""  # Article / Answer / "" (外部来源)
    ContentID: str
    ContentText: str = ""
    Url: str
    CommentCount: int = 0
    VoteUpCount: int = 0
    AuthorName: str = ""
    AuthorAvatar: str = ""
    AuthorBadge: str = ""
    AuthorBadgeText: str = ""
    EditTime: int  # unix timestamp
    AuthorityLevel: str = ""
    RankingScore: float = 0.0
    CommentInfoList: List[ZhihuCommentInfo] = []


class ZhihuData(BaseModel):
    HasMore: bool = False
    SearchHashId: str = ""
    Items: List[ZhihuSearchItem] = []


class ZhihuSearchResponse(BaseModel):
    Code: int
    Message: str
    Data: ZhihuData
