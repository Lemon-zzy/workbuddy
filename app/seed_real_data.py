"""种子数据 - 从真实知乎 API 响应灌入数据库

数据来源：知乎开放平台 workbuddy 搜索响应（用户提供）
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import init_db, SessionLocal
from app.models import Author, Content


# 真实数据 - 来自知乎开放平台 workbuddy 搜索结果
SEED_ITEMS = [
    {
        "Title": "腾讯混元 Hy3 + WorkBuddy 一手实测,Agent 能力提升不止一点 - 知乎",
        "ContentType": "Article",
        "ContentID": "-3949267257524928420",
        "ContentText": "大家好，我是小林。之前我写了好几篇 Claude Code 的教程，反响都很不错，不少朋友看到我的教程，也开始把 Claude Code 实操起来了。但是也有不是搞编程的朋友跟我吐槽，CC 这个上手门槛好高啊，这也太极客了，做啥事都得敲命令，我哪记得住，根本不会用。确实如此，CC 设计之初就不是给普通人设计的，所以对大多数人来说，极其不友好。那有没有适合大多数人用的 Agent 产品呢？那必须。",
        "Url": "https://zhuanlan.zhihu.com/p/2058159969808160440",
        "CommentCount": 0,
        "VoteUpCount": 8,
        "AuthorName": "小林coding",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-98f2e73c0d32161569ee7beb5b58ad55_l.jpg",
        "AuthorBadgeText": "AI编程开发等 2 个话题下的优秀答主",
        "AuthorityLevel": "4",
        "RankingScore": 3.5854578,
        "EditTime": 1783483842,
    },
    {
        "Title": "腾讯workbuddy大家平时主要用来做什么? - 知乎",
        "ContentType": "Answer",
        "ContentID": "-8368859931756937504",
        "ContentText": "不喜欢用国外的，就把它当国内的平替了。现在每天已离不开他，不管是商业计划书的编写，竞品分析报告，产品demo搭建，微文文案编写，skill技能生成，还是课件设计和PPT生成，甚至一些自动化的任务，几乎都靠他解决了，不敢想象么有AI的日子，感觉自己脑子都不会动了。",
        "Url": "https://www.zhihu.com/question/2056456330593023259/answer/2057847748641269323",
        "CommentCount": 0,
        "VoteUpCount": 1,
        "AuthorName": "爱喝咖啡的豆",
        "AuthorAvatar": "https://pica.zhimg.com/50/v2-c8a9afe61c218203529696eb410c2d24_l.jpg",
        "AuthorBadgeText": "",
        "AuthorityLevel": "4",
        "RankingScore": 3.5026643,
        "EditTime": 1783409136,
    },
    {
        "Title": "分享 WorkBuddy+蚁小二 CLI,全平台自媒体,从创作到运维都打通了 - 知乎",
        "ContentType": "Article",
        "ContentID": "-5804396609087737076",
        "ContentText": "前段时间我自己在做全平台的媒体运维工具，可以说是边做边改，边改边用。但这个过程很费脑子，而且费米米（tokens）。于是我就在想，现在有那么多强大的 Agent 工具，有没有可能我可以利用现成的平台和工具来做全平台的媒体运维呢！没想到，还真被我找到了。我用「WorkBuddy」加上「蚁小二」彻底跑通了全平台自媒体运营这个渠道，实现了内容辅助创作、内容自动核验、多平台多账号统一管理、入库发布。",
        "Url": "https://zhuanlan.zhihu.com/p/2058499815118468728",
        "CommentCount": 0,
        "VoteUpCount": 0,
        "AuthorName": "可爱的小Cherry",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-cde8d693e1240aefa136aa6a0d5f870e_l.jpg",
        "AuthorBadgeText": "知势榜成长力榜数码领域上榜答主",
        "AuthorityLevel": "4",
        "RankingScore": 3.4776819,
        "EditTime": 1783566062,
    },
    {
        "Title": "如何评价WorkBuddy? - 知乎",
        "ContentType": "Answer",
        "ContentID": "8101429738647388999",
        "ContentText": "正好WorkBuddy和隔壁字节的Trae最近都有在用。如果是写代码这种比较烧Token的任务，我还是更推荐Trae，现阶段它是按速通的会话次数收费，买个速通套餐需要排队的热门模型直接猛猛蹬，至于像MiniMax M3这种不用排队的那更是不交钱都随便用，总之没有Token焦虑是它的最大优势。而WorkBuddy虽然没有排队这一说，热门一线模型都能调用，但每个任务都是要消耗积分的，积分本质上就是。",
        "Url": "https://www.zhihu.com/question/2049048570800628238/answer/2057481664364798316",
        "CommentCount": 0,
        "VoteUpCount": 9,
        "AuthorName": "Nomore",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-0e8f02016e8644c1746d83fb27c6530c_l.jpg",
        "AuthorBadgeText": "知势榜影响力榜数码领域上榜答主",
        "AuthorityLevel": "4",
        "RankingScore": 3.4490707,
        "EditTime": 1783321854,
    },
    {
        "Title": "分享WorkBuddy+蚁小二 CLI,全平台自媒体,从创作到运维都打通了_服务软件_什么值得买",
        "ContentType": "",
        "ContentID": "-6818864694804798184",
        "ContentText": "前段时间我自己在做全平台的媒体运维工具，可以说是边做边改，边改边用。但这个过程很费脑子，而且费米米(tokens)。于是我就在想，现在有那么多强大的 Agent 工具，有没有可能我可以利用现成的平台和工具来做全平台的媒体运维呢!没想到，还真被我找到了。我用「WorkBuddy」加上「蚁小二」彻底跑通了全平台自媒体运营这个渠道，实现了内容辅助创作、内容自动核验、多平台多账号统一管理、入库发布、数。",
        "Url": "https://post.smzdm.com/p/am97zmxp/",
        "CommentCount": 0,
        "VoteUpCount": 0,
        "AuthorName": "可爱的小cherry",
        "AuthorAvatar": "",
        "AuthorBadgeText": "",
        "AuthorityLevel": "3",
        "RankingScore": 3.421832,
        "EditTime": 1783566566,
    },
    {
        "Title": "如何评价WorkBuddy? - 知乎",
        "ContentType": "Answer",
        "ContentID": "-4746232398107841940",
        "ContentText": '这年头，号称云端工作，结果移动端做了半天的工作，到PC端一看，数据完全没打通。AI产品多端打通不应该是基本的能力吗？没有云的能力能不能就别污辱"云端"这个概念？这么烂的体验，真的很久没碰到过了。这破玩意还想收钱，就凭你叫腾讯吗？',
        "Url": "https://www.zhihu.com/question/2049048570800628238/answer/2058347784252797098",
        "CommentCount": 2,
        "VoteUpCount": 1,
        "AuthorName": "小克",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-4ef3d20fc226f46fe10dae88ac969cbf_l.jpg",
        "AuthorBadgeText": "",
        "AuthorityLevel": "4",
        "RankingScore": 3.4137735,
        "EditTime": 1783528354,
    },
    {
        "Title": "Hy3调用激增、算力消耗达峰值,WorkBuddy:已扩容|hy|腾讯云|知名企业|系列模型价格|workbuddy_网易订阅",
        "ContentType": "",
        "ContentID": "-5432864193175167572",
        "ContentText": '新京报贝壳财经讯(记者韦英姿)腾讯Hy3已在WorkBuddy上线。7月9日，WorkBuddy和混元联合项目团队发布公告称，7月8日上午10时开始，算力资源消耗达到峰值，并出现排队情况，下午排队率一度超过 50%。"为了提供更好的Hy3使用体验和稳定服务，我们第一时间调度可用资源进行补充，目前已扩容完毕。"7月6日，腾讯正式发布Hy3。目前Hy3已在WorkBuddy/CodeBuddy、元宝。',
        "Url": "https://www.163.com/dy/article/L1D0EMFC0512D3VJ.html",
        "CommentCount": 0,
        "VoteUpCount": 0,
        "AuthorName": "新京报",
        "AuthorAvatar": "",
        "AuthorBadgeText": "",
        "AuthorityLevel": "3",
        "RankingScore": 3.410255,
        "EditTime": 1783564936,
    },
    {
        "Title": "如何看待腾讯 AI 工作台 WorkBuddy 的未来发展呢? - 知乎",
        "ContentType": "Answer",
        "ContentID": "-4389002437398201511",
        "ContentText": '目前WorkBuddy用起来还是挺强的。比如我就尝试用 WorkBuddy 搭了一套世界杯预测流程：先获取国际足球历史比赛数据，再构造球队特征，训练胜率分类器，最后模拟小组赛、32 强、16 强、8 强、半决赛和决赛，生成一份完整的 2026 世界杯晋级预测。当然，这不是"预言"，也不是说模型一定比人更懂球。现在AI这么强大，我们就可以充分使用AI进行一次数据驱动的世界杯推演：用历史数据和机器学习。',
        "Url": "https://www.zhihu.com/question/2055978055760344698/answer/2057230544195285674",
        "CommentCount": 2,
        "VoteUpCount": 2,
        "AuthorName": "算法一只狗",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-a5493fc49b661e53f2d5ea3c56009d68_l.jpg",
        "AuthorBadgeText": "深圳市腾讯计算机系统有限公司 员工",
        "AuthorityLevel": "4",
        "RankingScore": 3.3786983,
        "EditTime": 1783261983,
    },
    {
        "Title": "如何评价腾讯 WorkBuddy + 混元 3:不够惊艳?为什么腾讯感觉做不出特别好用的 AI 产品? - 知乎",
        "ContentType": "Answer",
        "ContentID": "6844358002608092532",
        "ContentText": "Hy3 我本以为会在Agent上有所不足，没想到一轮测下来表现还挺稳。虽然只有256k上下文窗口，但配合WorkBuddy还是能「稳稳接住」我的实测；第五个任务它只花了10分钟，是三个模型里效率最高的。最后是价格。国产模型在这方面都挺有性价比，而且也都开源。基本上，现在全球的开源模型就看中国了。",
        "Url": "https://www.zhihu.com/question/2057950830016435294/answer/2058106235044508896",
        "CommentCount": 0,
        "VoteUpCount": 2,
        "AuthorName": "Macode码客",
        "AuthorAvatar": "https://pic1.zhimg.com/50/v2-cb679d0afd91904a4aeae9e3ed6f4327_l.jpg",
        "AuthorBadgeText": "",
        "AuthorityLevel": "4",
        "RankingScore": 3.3680573,
        "EditTime": 1783470764,
    },
    {
        "Title": "workbuddy好用吗? - 知乎",
        "ContentType": "Answer",
        "ContentID": "-887110167053406520",
        "ContentText": "我自己对 WorkBuddy 的判断是：它好不好用，不能只看它内置了哪些模型，而要看它能不能稳定接入你真正想用的模型。WorkBuddy 本身是一个偏办公场景的桌面 Agent 客户端，适合做文档处理、资料整理、代码辅助、自动化办公这类任务。但很多人上手后会遇到一个问题：默认模型不一定总是最适合自己的场景。比如你写代码可能更喜欢 Claude，做中文长文可能想试 Kimi / GLM，做多模。",
        "Url": "https://www.zhihu.com/question/2040834090434356114/answer/2056521321396303860",
        "CommentCount": 1,
        "VoteUpCount": 5,
        "AuthorName": "崔庆才丨静觅",
        "AuthorAvatar": "https://picx.zhimg.com/50/v2-668df55dec9f0f11561a51c50693407c_l.jpg",
        "AuthorBadgeText": "",
        "AuthorityLevel": "4",
        "RankingScore": 3.34377,
        "EditTime": 1783092891,
    },
]


_TYPE_MAP = {"article": "article", "answer": "answer", "zvideo": "zvideo", "video": "zvideo", "": "external"}


def _build_excerpt(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").replace("\r", " ").strip()
    if len(text) > max_len:
        text = text[:max_len] + "…"
    return text


def _has_video_hint(text: str) -> bool:
    if not text:
        return False
    return any(k in text for k in ["视频", "实操", "演示", "点击观看", "播放"])


def seed(db: Session):
    print("开始灌入 seed 数据...")

    # 先清空（避免重复）
    db.query(Content).delete()
    db.query(Author).delete()
    db.commit()

    for item in SEED_ITEMS:
        # 作者
        author_id = f"u_{item['AuthorName'] or 'unknown'}"
        author = db.query(Author).filter(Author.id == author_id).first()
        if not author:
            author = Author(
                id=author_id,
                name=item["AuthorName"] or "未知作者",
                avatar=item.get("AuthorAvatar") or None,
                bio=item.get("AuthorBadgeText") or None,
                badge_text=item.get("AuthorBadgeText") or None,
                authority_level=item.get("AuthorityLevel") or "0",
                content_count=1,
                total_votes=item.get("VoteUpCount") or 0,
            )
            db.add(author)
        else:
            author.content_count = (author.content_count or 0) + 1
            author.total_votes = max(author.total_votes or 0, item.get("VoteUpCount") or 0)

        # 内容
        content_type = _TYPE_MAP.get((item.get("ContentType") or "").lower(), "external")
        edit_time = datetime.fromtimestamp(item["EditTime"]) if item.get("EditTime") else datetime.now()

        content = Content(
            id=item["ContentID"],
            type=content_type,
            title=item["Title"],
            excerpt=_build_excerpt(item.get("ContentText", "")),
            content_text=item.get("ContentText", ""),
            cover=None,
            source_url=item["Url"],
            author_id=author_id,
            author_name=item["AuthorName"] or "未知作者",
            author_avatar=item.get("AuthorAvatar") or None,
            voteup_count=item.get("VoteUpCount") or 0,
            comment_count=item.get("CommentCount") or 0,
            ranking_score=int((item.get("RankingScore") or 0) * 1000),
            has_video=_has_video_hint(item.get("ContentText", "")),
            comment_info=None,
            edit_time=edit_time,
        )
        db.add(content)

    db.commit()

    total = db.query(Content).count()
    authors = db.query(Author).count()
    videos = db.query(Content).filter(Content.has_video == True).count()
    print(f"✅ Seed 完成: {total} 条内容, {authors} 位作者, {videos} 个含视频记录")


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
