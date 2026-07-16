"""导出 DB 内容为 .md 文件 - 每篇一个 .md
目录结构: d:\\workbuddy专题\\content\\YYYY-MM\\YYYY-MM-DD_HHMM_<slug>.md
"""
import sys
import re
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, r"d:\workbuddy专题\backend")

from app.db.session import SessionLocal
from app.models import Content, Author

OUT_DIR = Path(r"d:\workbuddy专题\content")


def safe_filename(s: str, max_len: int = 60) -> str:
    """去掉文件名禁用字符"""
    s = re.sub(r'[\\/*?:"<>|]', '', s).strip()
    s = re.sub(r'\s+', '_', s)
    return s[:max_len]


def html_to_markdown(html: str) -> str:
    """简单 HTML → md 转换（够用即可）"""
    if not html:
        return ""
    import warnings
    from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

    soup = BeautifulSoup(html, "html.parser")

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-original") or img.get("data-actualsrc") or ""
        alt = img.get("alt", "")
        if src:
            md = f"\n\n![{alt}]({src})\n\n"
            img.replace_with(BeautifulSoup(f"<span>{md}</span>", "html.parser").span)

    for a in soup.find_all("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if href and text:
            md = f"[{text}]({href})"
            a.replace_with(BeautifulSoup(f"<span>{md}</span>", "html.parser").span)

    for br in soup.find_all("br"):
        br.replace_with("\n")

    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
        level = int(h.name[1])
        md = f"\n\n{'#' * level} {h.get_text(strip=True)}\n\n"
        h.replace_with(BeautifulSoup(md, "html.parser"))

    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if text:
            p.replace_with(BeautifulSoup(f"\n\n{text}\n\n", "html.parser"))

    for li in soup.find_all("li"):
        text = li.get_text().strip()
        li.replace_with(BeautifulSoup(f"\n- {text}", "html.parser"))

    for blockquote in soup.find_all("blockquote"):
        text = blockquote.get_text().strip()
        md = "\n\n" + "\n".join(f"> {line}" for line in text.splitlines()) + "\n\n"
        blockquote.replace_with(BeautifulSoup(md, "html.parser"))

    text = soup.get_text(separator="\n")
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def export_one(c: Content, author: Author) -> Path:
    """导出一篇 → 返回文件路径"""
    t = c.edit_time or c.fetched_at or c.created_at or datetime.now()
    if isinstance(t, str):
        try:
            t = datetime.fromisoformat(t)
        except (ValueError, TypeError):
            t = datetime.now()

    year_month = t.strftime("%Y-%m")
    date_str = t.strftime("%Y-%m-%d_%H%M")
    slug = safe_filename(c.title or f"untitled_{c.id}")
    month_dir = OUT_DIR / year_month
    month_dir.mkdir(parents=True, exist_ok=True)

    file_path = month_dir / f"{date_str}_{slug}.md"

    body_md = html_to_markdown(c.raw_html or "") if c.raw_html else (c.content_text or "")

    author_name = (author.name if author else c.author_name) or "未知作者"
    author_bio = (author.bio if author else None) or c.author_name or ""
    images = []
    if c.images_json:
        try:
            images = json.loads(c.images_json)
        except (ValueError, TypeError):
            images = []

    type_map = {"answer": "回答", "article": "文章", "zvideo": "视频", "question": "问题"}
    type_zh = type_map.get(c.type, c.type or "unknown")

    md = f"""---
id: {c.id}
type: {c.type}
type_zh: {type_zh}
title: "{c.title}"
author: "{author_name}"
author_bio: "{author_bio}"
source_url: {c.source_url}
voteup_count: {c.voteup_count or 0}
comment_count: {c.comment_count or 0}
has_video: {c.has_video or False}
images_count: {len(images)}
created_at: {t.isoformat()}
exported_at: {datetime.now().isoformat()}
---

# {c.title}

> {type_zh} · **{author_name}**
> {author_bio}
> 发布于 {t.strftime('%Y-%m-%d %H:%M')}
> 赞同 {c.voteup_count or 0} · 评论 {c.comment_count or 0}

## 摘要

{c.excerpt or '(无摘要)'}

## 正文

{body_md if body_md else '_(本篇目暂无正文)_'}

## 引用

```
{author_name} ({t.strftime('%Y-%m-%d')}). {c.title}. workbuddy 专题 · 知乎内容聚合.
原文链接: {c.source_url}
```

## 原文

[{c.source_url}]({c.source_url})

---

*本文件由 workbuddy 专题导出于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    file_path.write_text(md, encoding="utf-8")
    return file_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    db = SessionLocal()
    try:
        contents = db.query(Content).all()
        print(f"开始导出 {len(contents)} 条内容到 {OUT_DIR}")
        n_ok = n_empty = 0
        for i, c in enumerate(contents, 1):
            author = None
            if c.author_id:
                author = db.query(Author).filter(Author.id == c.author_id).first()
            try:
                p = export_one(c, author)
                n_ok += 1
                if i % 20 == 0 or i == 1:
                    print(f"  [{i}/{len(contents)}] {p.name}")
            except Exception as e:
                n_empty += 1
                print(f"  [{i}] 失败: {e}")
        print(f"\n✅ 导出完成: {n_ok} 个 md, {n_empty} 个失败")
        print(f"📁 位置: {OUT_DIR}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
