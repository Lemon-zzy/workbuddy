# workbuddy 专题 - 知乎内容聚合知识库

> 不用打开知乎，站内看完所有 workbuddy 相关干货

## 项目目标

从知乎数据开放平台（AccessKey）按"workbuddy"关键词抓取全站相关内容（回答 / 文章 / 视频），
聚合到一个**简洁但有记忆点**的知识库网页中，每日自动同步更新。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11 + FastAPI |
| 数据库 | SQLite（开发） / MySQL（生产） |
| 定时任务 | APScheduler |
| 数据源 | 知乎开放平台 API（AccessKey） |
| 前端 | Vue 3 + Vite + TypeScript |
| 风格 | Notion 底子 + 品牌色点缀 |

## 快速开始

### 1. 启动后端

```bash
cd backend
# Windows 直接双击 start.bat
start.bat
```

后端服务：`http://127.0.0.1:8000`
API 文档：`http://127.0.0.1:8000/docs`

### 2. 启动前端

```bash
cd frontend
# Windows 直接双击 start.bat
start.bat
```

前端页面：`http://127.0.0.1:5173`

### 3. 一键启动（推荐）

项目根目录双击 `start.bat`，同时启动前后端。

## 目录结构

```
workbuddy专题/
├── backend/          # Python FastAPI 后端
│   ├── app/
│   │   ├── api/      # 路由
│   │   ├── services/ # 业务逻辑（知乎 API 封装、解析）
│   │   ├── models/   # 数据库模型
│   │   ├── schemas/  # Pydantic
│   │   ├── db/       # 数据库连接
│   │   └── scheduler/# 定时任务
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Vue 3 前端
│   ├── src/
│   │   ├── views/    # 页面
│   │   ├── components/
│   │   ├── api/      # 后端 API 调用
│   │   ├── router/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.ts
└── start.bat         # 一键启动
```

## 开发进度

- [x] **M1**：项目骨架 + 假数据联调
- [ ] **M2**：知乎开放平台 API 接入
- [ ] **M3**：内容解析 + 数据库持久化
- [ ] **M4**：APScheduler 定时同步
- [ ] **M5**：前端视觉打磨（撕纸入场 / 视差 / 配色）
- [ ] **M6**：文档 + 部署

## 当前阶段

**M1 已完成**：可以浏览假数据的首页 / 列表 / 详情 / 搜索四个页面。
所有知乎内容均从 `backend/app/services/fake_data.py` 读取，M2 阶段切换为知乎 API 真实数据。

## 注意事项

- 知乎 AccessKey 需在 `backend/.env` 中配置（从 `.env.example` 复制）
- 试用 AccessKey 有调用额度限制，调试时注意控制请求频次
- 所有内容版权归原作者及知乎平台所有
