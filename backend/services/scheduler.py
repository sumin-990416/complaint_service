"""5분마다 전체 민원실 실시간 대기 데이터를 수집해 DB에 적재합니다."""
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.database import AsyncSessionLocal
from backend.models import QueueSnapshot
from backend.services.public_api import fetch_realtime

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def collect_queue_snapshots() -> None:
    now = datetime.now()
    try:
        data = await fetch_realtime()
    except Exception:
        return  # 공공 API 오류 시 조용히 넘어감

    async with AsyncSessionLocal() as db:
        for item in data["items"]:
            try:
                wtng = int(item.get("wtngCnt", 0))
            except (ValueError, TypeError):
                wtng = 0

            snap = QueueSnapshot(
                cso_sn=item.get("csoSn", ""),
                stdg_cd=item.get("stdgCd", ""),
                task_no=item.get("taskNo", ""),
                task_nm=item.get("taskNm"),
                wtng_cnt=wtng,
                collected_at=now,
                dow=now.weekday(),   # 0=월 … 6=일
                hour=now.hour,
            )
            db.add(snap)
        await db.commit()


def start_scheduler() -> None:
    scheduler.add_job(
        collect_queue_snapshots,
        trigger="interval",
        minutes=5,
        id="queue_collector",
        replace_existing=True,
    )
    # 매일 새벽 2시 모델 재학습 (쌓인 데이터로 GradientBoosting 학습)
    from backend.services.ml_model import retrain as ml_retrain

    async def retrain_job():
        result = await ml_retrain()
        logger.info("ML 재학습 결과: %s", result)

    scheduler.add_job(
        retrain_job,
        trigger="cron",
        hour=2,
        minute=0,
        id="ml_retrain",
        replace_existing=True,
    )
    scheduler.start()
