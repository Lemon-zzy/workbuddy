"""用用户提供的 URL 列表入库 - 抓详情 + 图片 + 评论 + 视频"""
import re
import json
import time
import random
import hashlib
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from app.services.html_cleaner import clean_zhihu_html
import httpx
from bs4 import BeautifulSoup


def _clean_text_simple(text: str) -> str:
    """清洗纯文本里的 markdown 残留（行首 #、粗体、链接等）"""
    if not text:
        return text
    text = re.sub(r'^\s*#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

from app.config import settings
from app.db.session import SessionLocal, init_db
from app.models import Author, Content


# 多套 UA，避免单一指纹
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


def _pick_ua() -> str:
    return random.choice(USER_AGENTS)


def _detect_type(url: str) -> str:
    if "/zvideo/" in url:
        return "zvideo"
    if "zhuanlan.zhihu.com/p/" in url:
        return "article"
    if "/question/" in url and "/answer/" in url:
        return "answer"
    if "/question/" in url:
        return "question"  # 题目主页
    return "external"


def _clean_url(url: str) -> str:
    if "?" not in url:
        return url
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        kept = {k: v[0] for k, v in qs.items() if not k.startswith("utm_") and k != "type"}
        return urlunparse(parsed._replace(query=urlencode(kept) if kept else ""))
    except Exception:
        return url


def _url_id(url: str) -> str:
    return "c_" + hashlib.md5(url.encode()).hexdigest()[:16]


def _req_headers(extra: dict = None) -> dict:
    h = {**DEFAULT_HEADERS, "User-Agent": _pick_ua()}
    if extra:
        h.update(extra)
    if settings.zhihu_cookie:
        h["Cookie"] = settings.zhihu_cookie
    return h


def _get_with_retry(client, url, referer, max_retry=3):
    """带指数退避的 GET，403/429 时睡长一些再试"""
    for i in range(max_retry):
        r = client.get(url, headers={"Referer": referer, "User-Agent": _pick_ua()})
        if r.status_code == 200:
            return r
        if r.status_code in (403, 429):
            wait = (2 ** i) * random.uniform(2.0, 4.0)  # 2-4s, 4-8s, 8-16s
            print(f"    [退避] {r.status_code}，等 {wait:.1f}s 重试...")
            time.sleep(wait)
            continue
        return r
    return r  # 最后一次


# ========== 详情抓取 ==========

def fetch_answer_page(url: str) -> dict:
    """抓回答详情页（question/.../answer/...）"""
    with httpx.Client(headers=_req_headers(), timeout=20.0, follow_redirects=True) as client:
        r = _get_with_retry(client, url, "https://www.zhihu.com/")
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        soup = BeautifulSoup(r.text, "html.parser")

        # 标题
        title = ""
        title_el = soup.select_one("h1.QuestionHeader-title")
        if title_el:
            title = title_el.get_text(strip=True)

        # 作者
        author_name = ""
        author_avatar = ""
        author_badge = ""
        # 多个可能的作者选择器
        for sel in [".AuthorInfo-name a", ".AuthorInfo-name", ".ContentItem-author .UserLink-link", ".UserLink-link"]:
            el = soup.select_one(sel)
            if el:
                author_name = el.get_text(strip=True)
                break
        badge_el = soup.select_one(".AuthorInfo-badgeText")
        if badge_el:
            author_badge = badge_el.get_text(strip=True)
        avatar_el = soup.select_one(".AuthorInfo-avatar img, .UserLink-avatar img")
        if avatar_el:
            author_avatar = avatar_el.get("src", "")

        # 正文
        body_html = ""
        body_text = ""
        body_el = soup.select_one(".RichText.ztext, .RichText--unescaped")
        if body_el:
            body_html = str(body_el)
            body_text = body_el.get_text("\n", strip=True)

        # 图片
        images = []
        if body_el:
            for img in body_el.select("img"):
                src = img.get("data-original") or img.get("data-actualsrc") or img.get("src", "")
                if src and src.startswith("http"):
                    images.append(src.split("?")[0])

        # 视频
        videos = []
        for video_el in soup.select("video source, video"):
            src = video_el.get("src") or video_el.get("data-src", "")
            if src:
                videos.append({"type": "video", "url": src, "title": title})
        for iframe in soup.select("iframe"):
            src = iframe.get("src", "")
            if "bilibili.com" in src or "v.qq.com" in src or "youtube.com" in src:
                videos.append({"type": "iframe", "url": src, "title": title})

        # 赞同
        voteup = 0
        for sel in [".VoteButton--up .VoteButton-count", "button[aria-label*='赞同']"]:
            el = soup.select_one(sel)
            if el:
                txt = el.get_text(strip=True)
                nums = re.findall(r"\d+", txt.replace(",", ""))
                if nums:
                    try:
                        voteup = int(nums[0])
                    except ValueError:
                        pass
                break

        # 评论数
        comments_count = 0
        comment_btn = soup.select_one("button[aria-label*='评论']")
        if comment_btn:
            txt = comment_btn.get_text(strip=True)
            nums = re.findall(r"\d+", txt)
            if nums:
                try:
                    comments_count = int(nums[0])
                except ValueError:
                    pass

        return {
            "ok": True, "title": title, "author_name": author_name,
            "author_avatar": author_avatar, "author_badge": author_badge,
            "body_html": body_html, "body_text": body_text,
            "images": images, "videos": videos, "voteup": voteup,
            "comments_count": comments_count,
        }


def fetch_question_page(url: str) -> dict:
    """抓问题主页（question/xxx）"""
    with httpx.Client(headers=_req_headers(), timeout=20.0, follow_redirects=True) as client:
        r = _get_with_retry(client, url, "https://www.zhihu.com/")
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        soup = BeautifulSoup(r.text, "html.parser")

        title = ""
        for sel in ["h1.QuestionHeader-title", ".QuestionHeader-title", "h1"]:
            el = soup.select_one(sel)
            if el:
                title = el.get_text(strip=True)
                break

        # 问题描述
        body_html = ""
        body_text = ""
        body_el = soup.select_one(".QuestionHeader-detail .RichText, .QuestionHeader .RichText")
        if body_el:
            body_html = str(body_el)
            body_text = body_el.get_text("\n", strip=True)

        # 找该问题下第一条回答
        first_answer = soup.select_one(".AnswerCard .RichText.ztext, .ContentItem .RichText")
        if first_answer and not body_text:
            body_html = str(first_answer)
            body_text = first_answer.get_text("\n", strip=True)

        return {
            "ok": True, "title": title, "author_name": "",
            "author_avatar": "", "author_badge": "",
            "body_html": body_html, "body_text": body_text,
            "images": [], "videos": [], "voteup": 0, "comments_count": 0,
        }


def fetch_article_page(url: str) -> dict:
    """抓文章详情页（zhuanlan.zhihu.com/p/xxx）"""
    with httpx.Client(headers=_req_headers(), timeout=20.0, follow_redirects=True) as client:
        r = _get_with_retry(client, url, "https://zhuanlan.zhihu.com/")
        if r.status_code != 200:
            return {"ok": False, "error": f"HTTP {r.status_code}"}
        soup = BeautifulSoup(r.text, "html.parser")

        title = ""
        for sel in ["h1.Post-Title", ".Post-Main h1", "h1"]:
            el = soup.select_one(sel)
            if el:
                title = el.get_text(strip=True)
                break

        author_name = ""
        for sel in [".AuthorInfo-name", ".Post-Author .UserLink-link", ".AuthorInfo a"]:
            el = soup.select_one(sel)
            if el:
                author_name = el.get_text(strip=True)
                break
        author_avatar = ""
        avatar_el = soup.select_one(".AuthorInfo-avatar img, .UserLink-avatar img")
        if avatar_el:
            author_avatar = avatar_el.get("src", "")

        body_html = ""
        body_text = ""
        body_el = soup.select_one(".Post-RichTextContainer, .RichText")
        if body_el:
            body_html = str(body_el)
            body_text = body_el.get_text("\n", strip=True)

        images = []
        if body_el:
            for img in body_el.select("img"):
                src = img.get("data-original") or img.get("data-actualsrc") or img.get("src", "")
                if src and src.startswith("http"):
                    images.append(src.split("?")[0])

        videos = []
        for iframe in (body_el.select("iframe") if body_el else []):
            src = iframe.get("src", "")
            if src:
                videos.append({"type": "iframe", "url": src, "title": title})

        return {
            "ok": True, "title": title, "author_name": author_name,
            "author_avatar": author_avatar, "author_badge": "",
            "body_html": body_html, "body_text": body_text,
            "images": images, "videos": videos, "voteup": 0, "comments_count": 0,
        }


# ========== 评论抓取 ==========

def fetch_comments(url: str, max_n: int = 20) -> list:
    m = re.search(r"/question/(\d+)/answer/(\d+)", url)
    if not m:
        return []
    answer_id = m.group(2)
    api = f"https://www.zhihu.com/api/v4/answers/{answer_id}/root_comments"
    with httpx.Client(headers=_req_headers(), timeout=15.0) as client:
        try:
            r = _get_with_retry(client, api + "?order=normal&limit=20&offset=0&status=open", url)
            if r.status_code != 200:
                return []
            data = r.json()
            return [
                {
                    "author_name": item.get("author", {}).get("name", ""),
                    "content": item.get("content", ""),
                    "voteup_count": item.get("vote_count", 0),
                    "created_at": item.get("created_time", 0),
                }
                for item in data.get("data", [])[:max_n]
            ]
        except Exception:
            return []


# ========== 入库 ==========

def upsert_one(db, url: str) -> str:
    """抓 URL 详情 + 入库"""
    url_type = _detect_type(url)

    if url_type == "answer":
        detail = fetch_answer_page(url)
    elif url_type == "article":
        detail = fetch_article_page(url)
    elif url_type == "question":
        detail = fetch_question_page(url)
    else:
        return "skipped"

    if not detail.get("ok"):
        print(f"  [失败] {url}: {detail.get('error')}")
        return "failed"

    # 抓评论
    comments = []
    if url_type == "answer" and detail.get("comments_count", 0) > 0:
        comments = fetch_comments(url, max_n=10)

    # ID
    url_id = _url_id(url)
    title = detail.get("title") or "无标题"
    body_text = detail.get("body_text", "")
    excerpt = (body_text[:200] + "…") if len(body_text) > 200 else body_text
    has_video = bool(detail.get("videos")) or "视频" in (title + body_text)

    # 作者
    author_id = f"u_{detail.get('author_name') or 'unknown'}"
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        author = Author(
            id=author_id,
            name=detail.get("author_name") or "未知作者",
            avatar=detail.get("author_avatar") or None,
            bio=detail.get("author_badge") or None,
            badge_text=detail.get("author_badge") or None,
            content_count=1,
            total_votes=detail.get("voteup", 0) or 0,
        )
        db.add(author)
    else:
        author.content_count = (author.content_count or 0) + 1
        author.total_votes = max(author.total_votes or 0, detail.get("voteup", 0) or 0)
        if not author.badge_text and detail.get("author_badge"):
            author.badge_text = detail["author_badge"]

    # 内容 upsert
    content = db.query(Content).filter(Content.id == url_id).first()
    if not content:
        content = Content(
            id=url_id,
            type=url_type,
            title=title,
            excerpt=excerpt,
            content_text=body_text,
            raw_html=detail.get("body_html", ""),
            images_json=json.dumps(detail.get("images", []), ensure_ascii=False),
            videos_json=json.dumps(detail.get("videos", []), ensure_ascii=False),
            comment_info=json.dumps(comments, ensure_ascii=False),
            cover=detail["images"][0] if detail.get("images") else None,
            source_url=_clean_url(url),
            author_id=author_id,
            author_name=detail.get("author_name") or "未知作者",
            author_avatar=detail.get("author_avatar") or None,
            voteup_count=detail.get("voteup", 0) or 0,
            comment_count=detail.get("comments_count", 0) or 0,
            has_video=has_video,
            edit_time=datetime.now(),
            fetched_via="crawler",
            crawl_status="ok",
        )
        db.add(content)
        status = "new"
    else:
        content.title = title
        # 清洗 excerpt / content_text（去掉行首 # 标题残留）
        content.excerpt = _clean_text_simple(excerpt)
        content.content_text = _clean_text_simple(body_text)
        # 清洗 raw_html（剥 style 块、知乎 class、行内 markdown）
        content.raw_html = clean_zhihu_html(detail.get("body_html", ""))
        content.images_json = json.dumps(detail.get("images", []), ensure_ascii=False)
        content.videos_json = json.dumps(detail.get("videos", []), ensure_ascii=False)
        content.comment_info = json.dumps(comments, ensure_ascii=False)
        content.voteup_count = max(content.voteup_count or 0, detail.get("voteup", 0) or 0)
        content.has_video = has_video
        content.fetched_via = "crawler"
        content.crawl_status = "ok"
        content.fetched_at = datetime.now()
        status = "updated"

    db.commit()
    return status


# ========== 入口 ==========

def crawl_urls(urls: list, sleep_s: float = 2.0):
    """主入口：URL 列表 → 抓详情 → 入库"""
    # 过滤掉搜索页 URL
    real_urls = [u for u in urls if "zhihu.com/search" not in u]
    print(f"[入库] 共 {len(real_urls)} 个 URL，过滤掉 {len(urls) - len(real_urls)} 个搜索页")

    init_db()
    db = SessionLocal()
    try:
        stats = {"new": 0, "updated": 0, "failed": 0, "skipped": 0}
        for i, url in enumerate(real_urls, 1):
            print(f"\n[{i}/{len(real_urls)}] {url[:80]}")
            try:
                status = upsert_one(db, url)
                stats[status] = stats.get(status, 0) + 1
                print(f"  → {status}")
            except Exception as e:
                print(f"  [异常] {e}")
                stats["failed"] += 1
                db.rollback()
            # 随机抖动：1.5x ~ 2.5x
            sleep_actual = sleep_s * random.uniform(0.8, 1.4)
            time.sleep(sleep_actual)

        print(f"\n✅ 完成: {stats}")
        print(f"   数据库: {db.query(Content).count()} 条内容 / {db.query(Author).count()} 位作者")
        return stats
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--urls":
        # 模式：直接接收 URL 列表
        urls = sys.argv[2].split(",")
        crawl_urls(urls)
    else:
        # 默认：用用户给的 23 个 URL
        urls = [
            "https://www.zhihu.com/question/2040834090434356114",
            "https://zhuanlan.zhihu.com/p/2058844008915509485",
            "https://www.zhihu.com/question/2016275980306645511",
            "https://www.zhihu.com/question/2049048570800628238/answer/2054027889021039452",
            "https://www.zhihu.com/question/2031424971629651052/answer/2058247168637642725",
            "https://zhuanlan.zhihu.com/p/2055276137723572615",
            "https://zhuanlan.zhihu.com/p/2058874469003834631",
            "https://www.zhihu.com/question/2049048570800628238/answer/2058347784252797098",
            "https://zhuanlan.zhihu.com/p/2058639663326401229",
            "https://zhuanlan.zhihu.com/p/2058698706602431440",
            "https://www.zhihu.com/question/2016275980306645511/answer/2040440410762371518",
            "https://www.zhihu.com/question/2016275980306645511/answer/2058124085952095309",
            "https://www.zhihu.com/question/2031424971629651052/answer/2042035112959796922",
            "https://www.zhihu.com/question/2057950830016435294/answer/2058106235044508896",
            "https://www.zhihu.com/question/2040834090434356114/answer/2058139072447637080",
            "https://zhuanlan.zhihu.com/p/2052455808143828816",
            "https://zhuanlan.zhihu.com/p/2058654176931062485",
            "https://zhuanlan.zhihu.com/p/2054983269926671903",
            "https://zhuanlan.zhihu.com/p/2048838508056404143",
            "https://zhuanlan.zhihu.com/p/2058548074256003541",
            "https://zhuanlan.zhihu.com/p/2058233468199424581",
        ]
        crawl_urls(urls)
