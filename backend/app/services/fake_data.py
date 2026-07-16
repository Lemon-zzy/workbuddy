"""M1 阶段假数据 - 用于前后端联调
M2 阶段会替换为知乎 API 真实数据
"""
from datetime import datetime, timedelta
from app.schemas.content import (
    ContentListItem,
    ContentDetail,
    AuthorOut,
    VideoOut,
)

# 假数据池
_AUTHORS = {
    "u_001": AuthorOut(
        id="u_001", name="AI产品观察",
        avatar="https://picsum.photos/seed/a1/80",
        bio="专注 AI 工具与生产力领域", follower_count=12453,
    ),
    "u_002": AuthorOut(
        id="u_002", name="程序员小张",
        avatar="https://picsum.photos/seed/a2/80",
        bio="全栈工程师 / 效率工具控", follower_count=3201,
    ),
    "u_003": AuthorOut(
        id="u_003", name="设计圈阿黎",
        avatar="https://picsum.photos/seed/a3/80",
        bio="用 WorkBuddy 做完整个项目的人", follower_count=8421,
    ),
    "u_004": AuthorOut(
        id="u_004", name="打工人自救指南",
        avatar="https://picsum.photos/seed/a4/80",
        bio="分享职场效率提升", follower_count=22890,
    ),
}

_CONTENTS = [
    {
        "id": "c_001",
        "type": "answer",
        "title": "WorkBuddy 到底好不好用？我用了 30 天后的真实感受",
        "excerpt": "作为每天和代码打交道的开发者，WorkBuddy 几乎重构了我的工作流。这篇文章会从真实使用场景出发，告诉你它到底值不值得入手……",
        "content_html": "<h2>前言</h2><p>WorkBuddy 是腾讯推出的一款 AI 生产力工具，深度集成 MCP 协议，能够连接你日常使用的 QQ 邮箱、腾讯会议、腾讯文档等生态……</p><h2>实际体验</h2><p>我连续使用了 30 天，主要场景包括：写代码、写文档、做设计、自动化任务……</p><blockquote>它最让我惊艳的不是某个功能，而是把所有工具串起来的能力。</blockquote>",
        "cover": "https://picsum.photos/seed/c1/1200/600",
        "source_url": "https://www.zhihu.com/question/xxxxx/answer/yyyyy",
        "author": _AUTHORS["u_001"],
        "voteup_count": 1287,
        "comment_count": 234,
        "created_at": datetime(2026, 6, 28, 10, 23),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "AI工具", "效率"],
        "has_video": False,
    },
    {
        "id": "c_002",
        "type": "zvideo",
        "title": "【视频教程】10 分钟学会用 WorkBuddy 接入微信公众号",
        "excerpt": "本期视频带大家从零开始，把 WorkBuddy 通过 MCP 协议接入微信公众号 API，实现'说一句，自动写爆款'的完整工作流……",
        "content_html": "<p>视频内容：<br>1. 准备工作：注册公众号、申请 API<br>2. WorkBuddy 配置 MCP 连接器<br>3. 设计 Prompt 模板<br>4. 实测效果展示</p>",
        "cover": "https://picsum.photos/seed/c2/1200/600",
        "source_url": "https://www.zhihu.com/zvideo/xxxxx",
        "author": _AUTHORS["u_003"],
        "voteup_count": 856,
        "comment_count": 89,
        "created_at": datetime(2026, 7, 2, 14, 5),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "MCP", "公众号"],
        "has_video": True,
        "video": VideoOut(
            id="v_001", title="10分钟学会WorkBuddy接入公众号",
            cover="https://picsum.photos/seed/v1/800/450",
            duration=612,
            play_url="https://www.zhihu.com/zvideo/xxxxx",
            embeddable=False,
        ),
    },
    {
        "id": "c_003",
        "type": "article",
        "title": "我把天眼查 MCP 接进了 WorkBuddy，信息差再也不存在了",
        "excerpt": "企业信息查询一直是打工人的痛点。现在我可以在 WorkBuddy 里直接问'这家公司股权结构是怎样的'，AI 自动决定调用哪些接口……",
        "content_html": "<h2>为什么需要这个</h2><p>做投资分析、求职背调、商业合作时，企业信息查询是刚需……</p><h2>配置步骤</h2><p>1. 申请天眼查 MCP 服务<br>2. 在 WorkBuddy 中添加连接器<br>3. 测试基础查询</p>",
        "cover": "https://picsum.photos/seed/c3/1200/600",
        "source_url": "https://zhuanlan.zhihu.com/p/xxxxx",
        "author": _AUTHORS["u_004"],
        "voteup_count": 2103,
        "comment_count": 412,
        "created_at": datetime(2026, 7, 5, 9, 12),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "MCP", "天眼查"],
        "has_video": False,
    },
    {
        "id": "c_004",
        "type": "answer",
        "title": "WorkBuddy vs Cursor vs Claude Code：三大 AI 编程工具横评",
        "excerpt": "作为同时在用这三款工具的开发者，我尽量客观地比较它们的优劣势，帮你找到最适合自己的那一款……",
        "content_html": "<h2>定位差异</h2><p>WorkBuddy 偏生产力套件，Cursor 专攻 IDE，Claude Code 走命令行路线……</p><h2>实测对比</h2><p>我从代码生成、调试、PR review、文档生成 4 个维度做了实测……</p>",
        "cover": "https://picsum.photos/seed/c4/1200/600",
        "source_url": "https://www.zhihu.com/question/yyyyy/answer/zzzzz",
        "author": _AUTHORS["u_002"],
        "voteup_count": 3421,
        "comment_count": 567,
        "created_at": datetime(2026, 7, 7, 16, 48),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "Cursor", "AI编程"],
        "has_video": False,
    },
    {
        "id": "c_005",
        "type": "zvideo",
        "title": "用 WorkBuddy + Ardot MCP 5 分钟生成完整设计系统",
        "excerpt": "设计师最痛苦的不是画图，是出规范。今天演示如何用 WorkBuddy 调度 Ardot 的 MCP，自动产出颜色、字号、组件库……",
        "content_html": "<p>视频演示：<br>1. 安装 Ardot 并登录<br>2. 在 WorkBuddy 中绑定 Ardot MCP<br>3. 一句话生成设计系统<br>4. 导出 Figma 资源</p>",
        "cover": "https://picsum.photos/seed/c5/1200/600",
        "source_url": "https://www.zhihu.com/zvideo/yyyyy",
        "author": _AUTHORS["u_003"],
        "voteup_count": 1789,
        "comment_count": 198,
        "created_at": datetime(2026, 7, 8, 11, 30),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "Ardot", "设计系统"],
        "has_video": True,
        "video": VideoOut(
            id="v_002", title="5分钟生成设计系统",
            cover="https://picsum.photos/seed/v2/800/450",
            duration=325,
            play_url="https://www.zhihu.com/zvideo/yyyyy",
            embeddable=False,
        ),
    },
    {
        "id": "c_006",
        "type": "article",
        "title": "WorkBuddy 全家桶干货：从连接到个性化设置一篇全讲完",
        "excerpt": "这篇文章把 WorkBuddy 所有值得知道的功能串起来：基础使用、连接器生态、个性化设置、效率技巧……",
        "content_html": "<h2>一、基础操作</h2><p>界面布局、对话技巧、模型选择……</p><h2>二、连接器</h2><p>基于 MCP 协议，WorkBuddy 能直接接入 QQ 邮箱、腾讯会议、腾讯文档……</p><h2>三、个性化</h2><p>偏好设置、记忆管理、团队空间……</p>",
        "cover": "https://picsum.photos/seed/c6/1200/600",
        "source_url": "https://zhuanlan.zhihu.com/p/yyyyy",
        "author": _AUTHORS["u_001"],
        "voteup_count": 567,
        "comment_count": 78,
        "created_at": datetime(2026, 7, 1, 20, 15),
        "fetched_at": datetime.now(),
        "tags": ["WorkBuddy", "教程", "干货"],
        "has_video": False,
    },
]


def get_all_contents() -> list[dict]:
    return _CONTENTS


def get_content_by_id(content_id: str) -> dict | None:
    for c in _CONTENTS:
        if c["id"] == content_id:
            return c
    return None
