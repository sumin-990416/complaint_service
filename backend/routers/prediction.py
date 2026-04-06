from fastapi import APIRouter, Query
from sqlalchemy import func, select

from backend.database import AsyncSessionLocal
from backend.models import QueueSnapshot
from backend.services.ml_model import predict as ml_predict

router = APIRouter(prefix="/prediction", tags=["prediction"])

DOW_KR = ["월", "화", "수", "목", "금", "토", "일"]


def _level(predicted: float) -> tuple[str, str, str]:
    if predicted < 3:
        return "여유", "🟢", "지금 바로 방문하기 좋아요!"
    elif predicted < 8:
        return "보통", "🟡", "약간의 대기가 있을 수 있어요"
    else:
        return "혼잡", "🔴", "대기 인원이 많을 수 있어요"


@router.get("/{cso_sn}")
async def get_prediction(
    cso_sn: str,
    dow: int = Query(..., ge=0, le=6, description="요일 (0=월 … 6=일)"),
    hour: int = Query(..., ge=0, le=23, description="시 (0~23)"),
):
    """특정 민원실의 요일·시간대 혼잡도 예측.
    ML 모델(GradientBoosting) 우선, 미학습 시 과거 평균 fallback.
    """
    async with AsyncSessionLocal() as db:
        cnt_result = await db.execute(
            select(func.count(QueueSnapshot.id))
            .where(QueueSnapshot.cso_sn == cso_sn)
        )
        sample_count = cnt_result.scalar() or 0

    # 1순위: ML 모델 예측
    ml_result = ml_predict(cso_sn, dow, hour)
    if ml_result is not None:
        level, emoji, msg = _level(ml_result)
        return {
            "predicted": ml_result,
            "level": level,
            "emoji": emoji,
            "message": f"{DOW_KR[dow]}요일 {hour}시 기준 {emoji} {msg}",
            "source": "ml",
            "sample_count": sample_count,
        }

    # 2순위: 과거 평균 fallback
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.avg(QueueSnapshot.wtng_cnt))
            .where(QueueSnapshot.cso_sn == cso_sn)
            .where(QueueSnapshot.dow == dow)
            .where(QueueSnapshot.hour == hour)
        )
        avg = result.scalar()

    if avg is None:
        return {
            "predicted": None,
            "level": "unknown",
            "message": "추후 업데이트 예정입니다",
            "source": "none",
            "sample_count": sample_count,
        }

    predicted = round(float(avg), 1)
    level, emoji, msg = _level(predicted)
    return {
        "predicted": predicted,
        "level": level,
        "emoji": emoji,
        "message": f"{DOW_KR[dow]}요일 {hour}시 기준 {emoji} {msg}",
        "source": "avg_fallback",
        "sample_count": sample_count,
    }


@router.post("/retrain")
async def trigger_retrain():
    """수동으로 ML 모델 재학습 트리거 (관리용)"""
    from backend.services.ml_model import retrain
    result = await retrain()
    return result
