"""知乎开放平台 API 客户端 - M2 实装版

接口分析（基于真实响应样本）：
- 平台域名: https://open.zhihu.com
- 搜索路径: /search
- 鉴权:    Authorization: Bearer {AccessKey}
- 必带参数: q (keyword), utm_source
- 返回结构: {Code, Message, Data{HasMore, SearchHashId, Items[]}}
"""
import httpx
from typing import Optional, List
from app.config import settings
from app.schemas.content import ZhihuSearchResponse, ZhihuSearchItem


class ZhihuClient:
    """知乎开放平台 API 客户端（同步版）"""

    def __init__(self):
        self.base_url = settings.zhihu_api_base
        self.search_path = settings.zhihu_search_path
        self.access_key = settings.zhihu_access_key
        self.utm_source = settings.zhihu_utm_source

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_key}",
            "Content-Type": "application/json",
            "User-Agent": "workbuddy-topic/0.1.0",
            "Accept": "application/json",
        }

    def search(
        self,
        keyword: str,
        limit: int = 10,
        search_hash_id: Optional[str] = None,
    ) -> ZhihuSearchResponse:
        """搜索接口（单次）"""
        params = {
            "q": keyword,
            "limit": limit,
            "utm_source": self.utm_source,
        }
        if search_hash_id:
            params["search_hash_id"] = search_hash_id

        with httpx.Client(base_url=self.base_url, timeout=30.0) as client:
            r = client.get(
                self.search_path,
                headers=self._headers(),
                params=params,
            )
            r.raise_for_status()
            return ZhihuSearchResponse(**r.json())

    def search_all(
        self,
        keyword: str,
        max_pages: int = 5,
        page_size: int = 10,
    ) -> List[ZhihuSearchItem]:
        """翻页拉取（最多 max_pages 页）"""
        first = self.search(keyword, limit=page_size)
        all_items = list(first.Data.Items)
        hash_id = first.Data.SearchHashId
        has_more = first.Data.HasMore

        for _ in range(max_pages - 1):
            if not has_more or not hash_id:
                break
            try:
                resp = self.search(keyword, limit=page_size, search_hash_id=hash_id)
                all_items.extend(resp.Data.Items)
                has_more = resp.Data.HasMore
                if not has_more:
                    break
            except Exception:
                # 翻页失败不致命，主结果已到手
                break

        return all_items


# 单例
zhihu_client = ZhihuClient()
