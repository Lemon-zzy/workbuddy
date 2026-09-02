"""配置管理 - 从 .env 读取，支持环境变量展开"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 知乎开放平台
    zhihu_access_key: str = ""
    zhihu_api_base: str = "https://open.zhihu.com"
    zhihu_search_path: str = "/search"
    zhihu_utm_source: str = "workbuddy-topic"

    # 服务
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = True

    # 数据库（支持 %TEMP% 等环境变量）
   database_url: str = "sqlite:////data/workbuddy.db"

    # 同步
    sync_keyword: str = "workbuddy"
    sync_cron_hour: int = 2
    sync_cron_minute: int = 0

    # 知乎网页端爬虫 Cookie（可选，访客态也能跑）
    zhihu_cookie: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # CORS 白名单（逗号分隔；* 表示全部允许；生产期限定 Vercel 域名）
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.cors_origins or "*").strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    # Render 部署：持久化数据目录（Render 磁盘）
    data_dir: str = "/data"
settings = Settings()
