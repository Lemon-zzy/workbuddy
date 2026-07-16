"""APScheduler 守护进程 - 长期跑在后台，每 N 小时抓一次
用法：
    python -m app.scheduler.daemon
    python -m app.scheduler.daemon --interval 6
"""
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apscheduler.schedulers.blocking import BlockingScheduler

from app.scheduler.daily_sync import run, DEFAULT_URL_FILE


def job():
    print(f"\n[{datetime.now().isoformat()}] 定时任务触发")
    run(DEFAULT_URL_FILE, sleep_s=3.0, keyword="apscheduler")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=6, help="间隔小时")
    args = ap.parse_args()

    sched = BlockingScheduler()
    sched.add_job(job, "interval", hours=args.interval, id="workbuddy_sync", next_run_time=datetime.now())
    print(f"启动守护进程，每 {args.interval} 小时跑一次")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("退出")
