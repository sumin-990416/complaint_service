from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import offices, realtime, prediction, chatbot
from backend.services.public_api import fetch_offices
from backend.services.scheduler import start_scheduler, scheduler
from backend.services.ml_model import retrain as ml_retrain
from backend import crud
from backend.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as db:
        existing = await crud.get_all_offices(db)
        if not existing:
            try:
                items = await fetch_offices()
                if items:
                    await crud.upsert_offices(db, items)
                    logger.info("공공 API 민원실 데이터 %d건 적재 완료", len(items))
            except Exception as e:
                logger.warning("공공 API 민원실 데이터 수집 실패: %s", e)

    # 수집된 데이터가 충분하면 ML 모델 학습 시도
    try:
        result = await ml_retrain()
        logger.info("서버 시작 시 ML 학습 결과: %s", result)
    except Exception as e:
        logger.warning("서버 시작 시 ML 학습 실패: %s", e)

    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="민원실 이용현황 API",
    description="행정안전부 민원실 기본정보 및 실시간 대기현황 서비스",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(offices.router, prefix="/api")
app.include_router(realtime.router, prefix="/api")
app.include_router(prediction.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs"}
