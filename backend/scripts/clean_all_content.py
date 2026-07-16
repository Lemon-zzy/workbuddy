"""一次性迁移：清洗所有 Content 的 raw_html + excerpt + content_text"""
import sys
import re
sys.path.insert(0, r"d:\workbuddy专题\backend")
from app.db.session import SessionLocal
from app.models import Content
from app.services.html_cleaner import clean_zhihu_html, count_hash_chars

def clean_text(text: str) -> str:
    """清洗纯文本里的 markdown 残留"""
    if not text:
        return text
    # 把行首 # 标题转成纯文本（去掉 # 号）
    text = re.sub(r'^\s*#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 粗体
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    # 斜体
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 链接 [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 多个空行收成 1 个
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

db = SessionLocal()
try:
    contents = db.query(Content).all()
    n_html_changed = 0
    n_excerpt_changed = 0
    n_text_changed = 0
    n_hash_removed = 0

    for c in contents:
        if c.raw_html:
            before = c.raw_html
            before_hashes = count_hash_chars(before)
            cleaned = clean_zhihu_html(before)
            after_hashes = count_hash_chars(cleaned)
            n_hash_removed += (before_hashes - after_hashes)
            if cleaned != before:
                c.raw_html = cleaned
                n_html_changed += 1

        if c.excerpt:
            cleaned = clean_text(c.excerpt)
            if cleaned != c.excerpt:
                c.excerpt = cleaned
                n_excerpt_changed += 1

        if c.content_text:
            cleaned = clean_text(c.content_text)
            if cleaned != c.content_text:
                c.content_text = cleaned
                n_text_changed += 1

    db.commit()
    print(f'raw_html 清洗修改: {n_html_changed}')
    print(f'excerpt 清洗修改: {n_excerpt_changed}')
    print(f'content_text 清洗修改: {n_text_changed}')
    print(f'共清理 {n_hash_removed} 个 # 颜色值')
finally:
    db.close()
