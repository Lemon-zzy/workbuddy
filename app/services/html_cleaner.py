"""知乎 HTML 清洗器
- 剥掉 <style> emotion-css 块（这就是满屏 # 颜色值的元凶）
- 剥掉知乎独有 class（.RichText, .ztext, .ContentItem...）
- 保留所有语义标签（h1-h6 / p / blockquote / ul / ol / img / a / code / pre / table）
- 修正 src → 绝对 URL
"""
import re
from bs4 import BeautifulSoup, Comment


def clean_zhihu_html(html: str) -> str:
    """把知乎原文 HTML 清洗成干净的正文 HTML"""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    # 1. 删掉所有 <style>（emotion-css 块、含 # 颜色值）
    for style in soup.find_all("style"):
        style.decompose()

    # 2. 删掉所有 <script>
    for script in soup.find_all("script"):
        script.decompose()

    # 3. 删掉所有 HTML 注释
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # 4. 删掉无意义包裹：<span class="RichText-... 仅有 css 的 span>
    for span in list(soup.find_all("span")):
        if not span.attrs:
            try:
                span.unwrap()
            except (ValueError, AttributeError):
                pass
            continue
        # 只删 class 全是 RichText-xxx 的、且没有别的属性
        classes = span.get("class") or []
        if classes and all("RichText" in c or "ztext" in c for c in classes):
            # 如果这个 span 没有内容或只有 inline children，剥掉但保留内容
            try:
                span.unwrap()
            except (ValueError, AttributeError):
                pass
            continue
        # 删掉空的 span（只有 whitespace）
        if not span.get_text(strip=True) and not span.find(["img", "br"]):
            span.decompose()

    # 5. 删掉知乎的脚注 / 推荐 / 编辑器装饰
    for sel in [
        ".RichText-Eyelet",        # 文末小灰字
        ".RichText-ContentEditable",
        ".RichText-DataSummary",
        ".ContentItem-actions",    # 点赞按钮
        ".BottomActions",
        ".ZVideoTag",
        ".Image-Wrapper-Preview",  # 图片遮罩
        ".RichText-Meta",
        "button",
        ".Modal-wrapper",
        "[data-action]",
        "noscript",
        "svg",
        "[aria-hidden='true']",
    ]:
        for el in soup.select(sel):
            el.decompose()

    # 6. 把知乎 class 替换为空（保留语义）
    for el in soup.find_all(True):
        if not el.attrs:
            continue
        # 删掉知乎特有 class
        if el.get("class"):
            cleaned = [c for c in el["class"]
                       if not any(prefix in c for prefix in [
                           "RichText", "ContentItem", "ztext", "AuthorInfo",
                           "Post-", "QuestionHeader", "css-", "DataLine",
                           "NumberBoard", "Button", "VoteButton",
                           "CommentItem", "Placeholder", "Popover",
                           "highlight", "Source", "Copyright",
                       ])]
            if cleaned:
                el["class"] = cleaned
            else:
                del el["class"]

        # 删掉知乎用的 inline style（除了少数有用的 align）
        style = el.get("style", "")
        if style:
            # 保留 color 是没用的（CSS-in-JS 残留），全清掉
            if "color" in style or "background" in style or "font" in style:
                del el["style"]

        # 删掉 data-* 标签
        for attr in list(el.attrs):
            if attr.startswith("data-") or attr in ("itemprop", "itemtype", "itemid", "itemscope"):
                del el[attr]

    # 7. 处理图片：保留 data-original/data-actualsrc 优先级，删 srcset
    for img in soup.find_all("img"):
        src = (img.get("data-original") or img.get("data-actualsrc")
               or img.get("data-default-watermark-src") or img.get("src", ""))
        # 去掉 ? 后缀
        src = src.split("?")[0] if "?" in src else src
        if src and src.startswith("//"):
            src = "https:" + src
        if src:
            img["src"] = src
        else:
            img.decompose()
            continue
        # 删掉 lazy load 类
        for attr in ["srcset", "data-srcset", "sizes", "loading"]:
            if attr in img.attrs:
                del img[attr]
        # 修 alt
        if not img.get("alt"):
            img["alt"] = ""

    # 8. 处理链接：把 href 里的 utm_/from 等追踪参数清掉
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if href and "?" in href:
            href = re.sub(r"[?&](utm_[^&]+|from[^&]*|source[^&]*|ab_test[^&]*)=([^&]*)", "", href)
            href = href.rstrip("?&")
        if href and href.startswith("//"):
            href = "https:" + href
        if href:
            a["href"] = href
        # 删 target rel 让站内行为可控
        if a.get("target") == "_blank":
            a["rel"] = "noopener"

    # 9. 处理 figure / 图片：把知乎的 Figure 改回纯 img
    for fig in soup.find_all("figure"):
        # 把 figure 内容（img + figcaption）保留
        pass

    # 10. 删掉知乎的 Nostalgia / 视频卡片装饰
    for sel in [".VideoCard", ".Image-Single", ".Image-Wrapper"]:
        for el in soup.select(sel):
            # 保留里面的 img
            imgs = el.find_all("img")
            for img in imgs:
                img.extract()
            # 把剩下的清空
            text = el.get_text(strip=True)
            if not text and not imgs:
                el.decompose()
            else:
                # 用文本 + 图片替换
                new_html = ""
                for img in imgs:
                    new_html += str(img)
                if text:
                    new_html += text
                new = BeautifulSoup(new_html, "html.parser")
                el.replace_with(new)

    # 11. 把空 p / div / section 全删
    for _ in range(3):  # 跑几遍，因为剥一个后里面的又变空了
        for el in soup.find_all(["p", "div", "section", "article"]):
            if not el.get_text(strip=True) and not el.find(["img", "br", "hr", "iframe", "video"]):
                el.decompose()

    # 12. 把 ugly <br><br> 收成 1 个
    for br in soup.find_all("br"):
        nxt = br.find_next_sibling()
        if nxt and nxt.name == "br":
            br.decompose()

    # 13. 把 <p> 里整段 markdown 文本（# ## ### 开头）转成真标签
    # 例: <p># 标题</p> -> <h1>标题</h1>
    for p in list(soup.find_all("p")):
        text = p.get_text(strip=True)
        if not text:
            continue
        m = re.match(r'^(#{1,6})\s+(.+)$', text)
        if m:
            level = len(m.group(1))
            new_tag = soup.new_tag(f"h{level}")
            new_tag.string = m.group(2).strip()
            p.replace_with(new_tag)
        else:
            # 把 #**加粗** 这种行内 markdown 简单处理
            inner = p.decode_contents()
            # 粗体 **text**
            inner = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', inner)
            # 斜体 *text*
            inner = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', inner)
            # 行内代码 `code`
            inner = re.sub(r'`([^`]+)`', r'<code>\1</code>', inner)
            # 链接 [text](url)
            inner = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', inner)
            new_fragment = BeautifulSoup(f"<root>{inner}</root>", "html.parser")
            # 把 root 的所有孩子移到原位置
            for child in list(new_fragment.root.children):
                p.insert_before(child.extract() if hasattr(child, 'extract') else new_fragment.new_string(str(child)))
            p.decompose()

    # 14. 删多余空 div（嵌套 div 里只有 1 个子元素）
    for _ in range(3):
        for div in soup.find_all("div"):
            children = list(div.children)
            # 只有 1 个孩子且是 div/p
            if len(children) == 1 and hasattr(children[0], 'name') and children[0].name in ('div', 'p', 'span'):
                div.unwrap()
            # 完全空
            elif not div.get_text(strip=True) and not div.find(['img', 'iframe', 'video', 'br', 'hr']):
                div.decompose()

    result = str(soup)
    # 合并连续空白
    result = re.sub(r'[\t ]+', ' ', result)
    result = re.sub(r'\n\s*\n', '\n', result)
    return result.strip()


def count_hash_chars(html: str) -> int:
    """统计 # 颜色值的数量（用于诊断）"""
    return len(re.findall(r'#[0-9A-Fa-f]{3,8}\b', html))
