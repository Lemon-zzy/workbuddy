"""统计相关路由"""
from fastapi import APIRouter
from app.services.fake_data import _CONTENTS
from datetime import datetime, timedelta
from collections import Counter

router = APIRouter()


@router.get("/timeline")
async def get_timeline(days: int = 30):
    """时间线分布 - 用于图表"""
    today = datetime.now()
    start = today - timedelta(days=days)
    buckets = Counter()
    for c in _CONTENTS:
        d = c["created_at"]
        if d >= start:
            key = d.strftime("%Y-%m-%d")
            buckets[key] += 1

    # 补齐缺失日期
    items = []
    for i in range(days):
        d = (today - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        items.append({"date": d, "count": buckets.get(d, 0)})
    return {"items": items}


@router.get("/tags")
async def get_tag_cloud():
    """标签云"""
    counter = Counter()
    for c in _CONTENTS:
        for t in c.get("tags", []):
            counter[t] += 1
    return {
        "items": [{"tag": t, "count": n} for t, n in counter.most_common(20)]
    }
