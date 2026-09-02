"""workbuddy 专题 - 部署指南 (Vercel + Render)

═══════════════════════════════════════════
  架构
═══════════════════════════════════════════

┌──────────────┐   /api/*   ┌──────────────┐
│   Vercel     │ ─────────▶ │   Render     │
│  (前端 Vue)  │            │ (FastAPI)    │
│  静态资源     │            │  + SQLite    │
└──────────────┘            └──────────────┘

═══════════════════════════════════════════
  第一步: 准备 GitHub 仓库
═══════════════════════════════════════════

1. 访问 https://github.com/new
2. 仓库名: workbuddy-zhuanlan
3. 不要勾选 Add README / .gitignore / license
4. 创建

═══════════════════════════════════════════
  第二步: 推代码到 GitHub
═══════════════════════════════════════════

在你电脑 PowerShell 跑:

    cd C:\Users\HUAWEI\workbuddy专题
    git remote add origin git@github.com:你的用户名/workbuddy-zhuanlan.git
    git branch -M main
    git push -u origin main

（推送时需要先在 https://github.com/settings/keys 加 SSH 公钥）

═══════════════════════════════════════════
  第三步: 部署后端到 Render
═══════════════════════════════════════════

1. 访问 https://render.com 用 GitHub 登录
2. 点 "New +" → "Blueprint"
3. 选择你的仓库 workbuddy-zhuanlan
4. Render 自动识别 render.yaml
5. 等待 build 完成（首次约 3-5 分钟）
6. 拿到后端 URL，类似：
   https://workbuddy-api-xxxx.onrender.com

═══════════════════════════════════════════
  第四步: 部署前端到 Vercel
═══════════════════════════════════════════

1. 访问 https://vercel.com 用 GitHub 登录
2. 点 "Add New" → "Project"
3. 导入 workbuddy-zhuanlan 仓库
4. 配置:
   - Framework Preset: Vite
   - Root Directory: frontend
   - Build Command: npm run build
   - Output Directory: dist
5. 点 Deploy
6. 部署完成

═══════════════════════════════════════════
  第五步: 修改 vercel.json 的后端地址
═══════════════════════════════════════════

打开 vercel.json，把:

    "destination": "https://workbuddy-api.onrender.com/api/$1"

改成你 Render 的实际后端 URL（不含尾部斜杠）。

然后重新部署 Vercel（自动触发 git push 即可）。

═══════════════════════════════════════════
  验证
═══════════════════════════════════════════

1. 访问 Vercel 提供的 URL
2. 页面应正常加载（首页 / 列表 / 详情 / md 库）
3. 数据从 Render 后端获取
4. 后端 /docs 显示 API 文档

═══════════════════════════════════════════
  注意事项
═══════════════════════════════════════════

- Render 免费版会在 15 分钟无请求后休眠, 首次访问可能慢
- 数据库用 SQLite, 数据存 Render 磁盘（重启不丢，免费版磁盘在 90 天后会清空）
- 如需持久化: 升级 Render 到 $7/月 plan（持久磁盘） 或用 Render Postgres
- 定时任务（每日同步）需要在 Render 后台进程层开启，free plan 不支持
"""
