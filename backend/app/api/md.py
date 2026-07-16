"""md 文件库 - 含 zip 下载、重新导出、HTML 渲染"""
import os
import re
import io
import zipfile
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

CONTENT_DIR = Path(r"d:\workbuddy专题\content")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    fm = {}
    body = content
    if content.startswith("---\n"):
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
        if m:
            fm_text = m.group(1)
            body = m.group(2)
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
    return fm, body


def parse_date_from_filename(name: str) -> Optional[datetime]:
    m = re.match(r"^(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})_", name)
    if m:
        try:
            return datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return None
    return None


def md_to_html(md_text: str) -> str:
    """简单 md → html（不依赖第三方）"""
    html = md_text

    # 跳过 frontmatter
    if html.startswith("---\n"):
        m = re.match(r"^---\n.*?\n---\n(.*)$", html, re.DOTALL)
        if m:
            html = m.group(1)

    lines = html.split("\n")
    out = []
    in_code = False
    code_buffer = []
    in_list = False
    list_type = None

    def flush_list():
        nonlocal in_list, list_type, out
        if in_list:
            out.append(f"</{list_type}>")
            in_list = False
            list_type = None

    for line in lines:
        # 代码块
        if line.strip().startswith("```"):
            if not in_code:
                flush_list()
                in_code = True
                lang = line.strip()[3:].strip()
                out.append(f'<pre class="md-code"><code class="lang-{lang}">')
            else:
                in_code = False
                out.append("</code></pre>")
            continue
        if in_code:
            code_buffer.append(line)
            out.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        stripped = line.strip()

        # 标题
        h_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if h_match:
            flush_list()
            level = len(h_match.group(1))
            text = h_match.group(2)
            out.append(f"<h{level}>{escape_html(text)}</h{level}>")
            continue

        # 引用
        if stripped.startswith(">"):
            flush_list()
            text = stripped[1:].strip()
            out.append(f"<blockquote>{escape_html(text)}</blockquote>")
            continue

        # 无序列表
        ul_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if ul_match:
            if not in_list or list_type != "ul":
                flush_list()
                out.append("<ul>")
                in_list = True
                list_type = "ul"
            out.append(f"<li>{format_inline(ul_match.group(1))}</li>")
            continue

        # 有序列表
        ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ol_match:
            if not in_list or list_type != "ol":
                flush_list()
                out.append("<ol>")
                in_list = True
                list_type = "ol"
            out.append(f"<li>{format_inline(ol_match.group(1))}</li>")
            continue

        # 分割线
        if re.match(r"^[-*_]{3,}$", stripped):
            flush_list()
            out.append("<hr>")
            continue

        # 空行
        if not stripped:
            flush_list()
            continue

        # 普通段落
        flush_list()
        out.append(f"<p>{format_inline(stripped)}</p>")

    flush_list()
    return "\n".join(out)


def format_inline(text: str) -> str:
    """处理粗体、斜体、代码、链接、图片"""
    text = escape_html(text)
    # 链接 [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # 图片 ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" loading="lazy">', text)
    # 粗体 **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # 斜体 *text*
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    # 行内代码 `code`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ========== 路由 ==========

@router.get("/list")
async def list_md_files(
    year_month: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    if not CONTENT_DIR.exists():
        return {"total": 0, "items": []}

    files = []
    for p in CONTENT_DIR.rglob("*.md"):
        if year_month and year_month not in p.parts:
            continue
        rel = p.relative_to(CONTENT_DIR)
        name = p.stem
        date = parse_date_from_filename(p.name)
        if not date:
            date = datetime.fromtimestamp(p.stat().st_mtime)
        files.append({
            "path": str(rel).replace("\\", "/"),
            "filename": p.name,
            "name": name,
            "size": p.stat().st_size,
            "mtime": date.isoformat(),
            "year_month": date.strftime("%Y-%m"),
        })

    files.sort(key=lambda x: x["mtime"], reverse=True)

    if keyword:
        kw = keyword.lower()
        files = [f for f in files if kw in f["name"].lower() or kw in f["filename"].lower()]

    total = len(files)
    page = files[offset:offset + limit]
    return {"total": total, "items": page}


@router.get("/months")
async def list_months():
    if not CONTENT_DIR.exists():
        return {"items": []}
    months = set()
    for p in CONTENT_DIR.iterdir():
        if p.is_dir() and re.match(r"^\d{4}-\d{2}$", p.name):
            months.add(p.name)
    return {"items": sorted(months, reverse=True)}


@router.get("/search")
async def search_md(
    q: str = "",
    limit: int = 20,
    offset: int = 0,
    context_chars: int = 80,
):
    """md 全文搜索 - 跨所有 .md 搜关键词
    - 返回每处命中所在行、文件、上下文片段
    - 高亮用 <mark> 包裹（前端用 v-html 安全）
    """
    if not q or not q.strip():
        return {"total": 0, "items": [], "q": q}

    if not CONTENT_DIR.exists():
        return {"total": 0, "items": [], "q": q}

    q_lower = q.lower()
    hits = []  # [{path, filename, title, year_month, mtime, line_no, snippet, count}]

    for p in CONTENT_DIR.rglob("*.md"):
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if q_lower not in content.lower():
            continue
        # 解析 frontmatter
        fm, body = parse_frontmatter(content)
        title = fm.get("title", p.stem)
        author = fm.get("author", "")

        # 按行查找
        lines = body.split("\n")
        line_hits = []
        total_count = 0
        for i, line in enumerate(lines, 1):
            cnt = line.lower().count(q_lower)
            if cnt > 0:
                total_count += cnt
                # 截取上下文
                idx = line.lower().find(q_lower)
                start = max(0, idx - context_chars)
                end = min(len(line), idx + len(q) + context_chars)
                snippet = line[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(line):
                    snippet = snippet + "..."
                # 高亮（保留原文大小写不破坏）
                hl = re.sub(
                    re.escape(q),
                    lambda m: f"<mark>{m.group(0)}</mark>",
                    snippet,
                    flags=re.IGNORECASE,
                )
                line_hits.append({
                    "line_no": i,
                    "snippet": hl,
                    "count": cnt,
                })

        if total_count == 0 and not line_hits:
            # 只有 frontmatter 含，但 body 没找到
            continue

        # 摘要用 frontmatter 的 excerpt
        excerpt = fm.get("excerpt", "") or body[:200]

        date = parse_date_from_filename(p.name)
        if not date:
            date = datetime.fromtimestamp(p.stat().st_mtime)

        rel = p.relative_to(CONTENT_DIR)
        hits.append({
            "path": str(rel).replace("\\", "/"),
            "filename": p.name,
            "title": title.strip('"') if isinstance(title, str) else title,
            "author": author.strip('"') if isinstance(author, str) else author,
            "year_month": date.strftime("%Y-%m"),
            "mtime": date.isoformat(),
            "excerpt": excerpt[:200],
            "line_hits": line_hits[:10],  # 最多 10 处
            "total_count": total_count,
        })

    # 按命中数排序
    hits.sort(key=lambda x: x["total_count"], reverse=True)
    total = len(hits)
    page = hits[offset:offset + limit]

    return {
        "total": total,
        "items": page,
        "q": q,
        "limit": limit,
        "offset": offset,
    }


@router.get("/raw/{path:path}")
async def read_md_file(path: str, format: Optional[str] = "raw"):
    """format: raw | html | both"""
    full = (CONTENT_DIR / path).resolve()
    if not str(full).startswith(str(CONTENT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="路径越界")
    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")

    raw = full.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw)

    result = {
        "path": path,
        "filename": full.name,
        "size": full.stat().st_size,
        "mtime": datetime.fromtimestamp(full.stat().st_mtime).isoformat(),
        "frontmatter": fm,
    }
    if format in ("raw", "both"):
        result["raw"] = raw
    if format in ("html", "both"):
        result["html"] = md_to_html(raw)
    return result


@router.get("/download/{path:path}")
async def download_md_file(path: str):
    """下载单个 md 文件"""
    full = (CONTENT_DIR / path).resolve()
    if not str(full).startswith(str(CONTENT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="路径越界")
    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")

    content = full.read_text(encoding="utf-8")
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=\"md.md\"; filename*=UTF-8''{quote(full.name)}",
        },
    )


@router.get("/download_zip")
async def download_zip(
    year_month: Optional[str] = None,
    keyword: Optional[str] = None,
):
    """批量下载为 zip（可按月份/关键词过滤）"""
    if not CONTENT_DIR.exists():
        raise HTTPException(status_code=404, detail="文件库为空")

    files = []
    for p in CONTENT_DIR.rglob("*.md"):
        if year_month and year_month not in p.parts:
            continue
        rel = p.relative_to(CONTENT_DIR)
        name = p.stem
        if keyword and (keyword.lower() not in name.lower() and keyword.lower() not in p.name.lower()):
            continue
        files.append((p, rel))

    if not files:
        raise HTTPException(status_code=404, detail="无匹配文件")

    buf = io.BytesIO()
    suffix = f"_{year_month}" if year_month else ""
    zip_name = f"workbuddy_md{suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}.zip"
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, rel in files:
            zf.write(full, arcname=str(rel).replace("\\", "/"))
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_name}"'},
    )


@router.post("/reexport")
async def reexport():
    """重新导出所有内容到 md（异步执行）"""
    script = r"d:\workbuddy专题\backend\scripts\export_to_md.py"
    if not Path(script).exists():
        raise HTTPException(status_code=404, detail="导出脚本不存在")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, timeout=300,
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-500:],
            "stderr_tail": result.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="导出超时")
