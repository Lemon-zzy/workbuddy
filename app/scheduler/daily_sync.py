"""M3 定时同步脚本 - standalone
- 从 URL 列表文件读 URL
- 调爬虫抓详情 + 入库
- 写 sync_log
- 可以被 Windows Task Scheduler / cron 调起

用法：
    python -m app.scheduler.daily_sync              # 读默认 URL 列表
    python -m app.scheduler.daily_sync --file X.txt  # 指定 URL 文件
"""
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db.session import SessionLocal, init_db
from app.services.crawler import upsert_one
from app.models import SyncLog


DEFAULT_URL_FILE = Path(__file__).resolve().parents[2] / "data" / "seed_urls.txt"
DEFAULT_SLEEP_S = 3.0


def load_urls(file_path: Path) -> list:
    if not file_path.exists():
        print(f"URL 文件不存在: {file_path}")
        return []
    with open(file_path, encoding="utf-8") as f:
        urls = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    return urls


def run(file_path: Path, sleep_s: float = DEFAULT_SLEEP_S, keyword: str = "scheduled") -> int:
    """主流程，返回入库条数（new+updated）"""
    init_db()
    urls = load_urls(file_path)
    if not urls:
        print("无 URL 可处理")
        return 0

    print(f"[{datetime.now().isoformat()}] 开始同步 {len(urls)} 条 URL（来自 {file_path.name}）")

    db = SessionLocal()
    log = SyncLog(status="running", keyword=keyword)
    db.add(log)
    db.commit()
    db.refresh(log)

    new_n = updated_n = failed_n = 0
    try:
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url[:80]}", flush=True)
            try:
                status = upsert_one(db, url)
                if status == "new":
                    new_n += 1
                elif status == "updated":
                    updated_n += 1
                else:
                    failed_n += 1
            except Exception as e:
                failed_n += 1
                db.rollback()
                print(f"    异常: {e}", flush=True)
            time.sleep(sleep_s)

        log.fetched_count = len(urls)
        log.new_count = new_n
        log.updated_count = updated_n
        log.status = "success"
    except Exception as e:
        log.status = "failed"
        log.error_message = str(e)[:500]
    finally:
        log.finished_at = datetime.now()
        db.commit()
        db.refresh(log)
        db.close()

    print(f"[{datetime.now().isoformat()}] 完成: new={new_n} updated={updated_n} failed={failed_n}")
    print(f"  log_id={log.id} status={log.status}")
    return new_n + updated_n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", type=Path, default=DEFAULT_URL_FILE, help="URL 列表文件")
    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_S, help="间隔秒数（防风控）")
    ap.add_argument("--keyword", type=str, default="scheduled", help="日志标记")
    args = ap.parse_args()
    run(args.file, args.sleep, args.keyword)
