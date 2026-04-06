"""
혼잡도 예측 ML 모델 서비스

학습 전략:
- 매일 새벽 2시 스케줄러가 retrain() 호출
- 학습 데이터: QueueSnapshot 전체 (dow, hour, cso_sn → wtng_cnt)
- 알고리즘: GradientBoostingRegressor (비선형 패턴 + 적은 데이터에서도 안정적)
- 모델 저장: models/queue_predictor.joblib
- 최소 데이터: 30개 이상일 때만 학습, 미만이면 avg fallback
"""
import os
import asyncio
import logging
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import select

from backend.database import AsyncSessionLocal
from backend.models import QueueSnapshot

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "queue_predictor.joblib"
ENCODER_PATH = MODEL_DIR / "cso_encoder.joblib"

MIN_SAMPLES = 30  # 학습에 필요한 최소 데이터 수

# 인메모리 모델 캐시 (서버 재시작 시 파일에서 로드)
_model: GradientBoostingRegressor | None = None
_encoder: LabelEncoder | None = None
_model_trained = False  # 한 번이라도 학습됐는지


def _load_from_disk() -> bool:
    global _model, _encoder, _model_trained
    if MODEL_PATH.exists() and ENCODER_PATH.exists():
        try:
            _model = joblib.load(MODEL_PATH)
            _encoder = joblib.load(ENCODER_PATH)
            _model_trained = True
            logger.info("ML 모델 로드 완료 (%s)", MODEL_PATH)
            return True
        except Exception as e:
            logger.warning("ML 모델 로드 실패: %s", e)
    return False


def _save_to_disk() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(_model, MODEL_PATH)
    joblib.dump(_encoder, ENCODER_PATH)
    logger.info("ML 모델 저장 완료")


def predict(cso_sn: str, dow: int, hour: int) -> float | None:
    """예측값 반환. 모델 미학습 시 None 반환 → 라우터에서 avg fallback."""
    global _model, _encoder, _model_trained

    if not _model_trained:
        _load_from_disk()

    if not _model_trained or _model is None or _encoder is None:
        return None

    try:
        # 학습 때 본 적 없는 cso_sn은 fallback
        if cso_sn not in _encoder.classes_:
            return None
        cso_encoded = _encoder.transform([cso_sn])[0]
        X = np.array([[dow, hour, cso_encoded]])
        result = _model.predict(X)[0]
        return max(0.0, round(float(result), 1))
    except Exception as e:
        logger.warning("ML 예측 오류: %s", e)
        return None


async def retrain() -> dict:
    """전체 QueueSnapshot으로 모델 재학습. 스케줄러에서 호출."""
    global _model, _encoder, _model_trained

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                QueueSnapshot.cso_sn,
                QueueSnapshot.dow,
                QueueSnapshot.hour,
                QueueSnapshot.wtng_cnt,
            )
        )
        rows = result.all()

    if len(rows) < MIN_SAMPLES:
        logger.info("ML 학습 스킵: 데이터 %d개 (최소 %d개 필요)", len(rows), MIN_SAMPLES)
        return {"status": "skipped", "reason": f"데이터 부족 ({len(rows)}개)", "samples": len(rows)}

    # numpy 배열로 변환
    cso_sns = [r.cso_sn for r in rows]
    dows = [r.dow for r in rows]
    hours = [r.hour for r in rows]
    wtng_cnts = [r.wtng_cnt for r in rows]

    # cso_sn 레이블 인코딩
    encoder = LabelEncoder()
    cso_encoded = encoder.fit_transform(cso_sns)

    X = np.column_stack([dows, hours, cso_encoded])
    y = np.array(wtng_cnts, dtype=float)

    # GradientBoosting: 비선형 패턴 학습, 과적합 방지 (max_depth=3)
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        random_state=42,
    )

    # 동기 sklearn 학습을 스레드풀에서 실행 (이벤트 루프 블로킹 방지)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, model.fit, X, y)

    _model = model
    _encoder = encoder
    _model_trained = True
    _save_to_disk()

    logger.info("ML 모델 재학습 완료: 샘플 %d개, 민원실 %d곳", len(rows), len(encoder.classes_))
    return {
        "status": "ok",
        "samples": len(rows),
        "offices": len(encoder.classes_),
    }
