from fastapi import APIRouter, Query
from sqlalchemy import func, select

from backend.database import AsyncSessionLocal
from backend.models import QueueSnapshot

router = APIRouter(prefix="/prediction", tags=["prediction"])

DOW_KR = ["월", "화", "수", "목", "금", "토", "일"]


@router.get("/{cso_sn}")
async def get_prediction(
    cso_sn: str,
    dow: int = Query(..., ge=0, le=6, description="요일 (0=월 … 6=일)"),
    hour: int = Query(..., ge=0, le=23, description="시 (0~23)"),
):
    """특정 민원실의 요일·시간대 평균 대기 인원(과거 데이터 기반) 반환"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.avg(QueueSnapshot.wtng_cnt))
            .where(QueueSnapshot.cso_sn == cso_sn)
            .where(QueueSnapshot.dow == dow)
            .where(QueueSnapshot.hour == hour)
        )
        avg = result.scalar()

        # 수집된 총 샘플 수
        cnt_result = await db.execute(
            select(func.count(QueueSnapshot.id))
            .where(QueueSnapshot.cso_sn == cso_sn)
        )
        sample_count = cnt_result.scalar() or 0

    if avg is None:
        return {
            "predicted": None,
            "level": "unknown",
            "message": "아직 데이터를 수집 중이에요.\n잠시 후 다시 확인해주세요.",
            "sample_count": sample_count,
        }

    predicted = round(float(avg), 1)

    if predicted < 3:
        level, emoji, msg = "여유", "🟢", "지금 바로 방문하기 좋아요!"
    elif predicted < 8:
        level, emoji, msg = "보통", "🟡", "약간의 대기가 있을 수 있어요"
    else:
        level, emoji, msg = "혼잡", "🔴", "대기 인원이 많을 수 있어요"

    return {
        "predicted": predicted,
        "level": level,
        "emoji": emoji,
        "message": f"{DOW_KR[dow]}요일 {hour}시 기준 {emoji} {msg}",
        "sample_count": sample_count,
    }
