from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import offices, realtime, prediction, chatbot
from backend.services.public_api import fetch_offices
from backend.services.scheduler import start_scheduler, scheduler
from backend import crud
from backend.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # 서버 시작 시 DB가 비어 있으면 공공 API에서 민원실 정보 자동 시드
    async with AsyncSessionLocal() as db:
        existing = await crud.get_all_offices(db)
        if not existing:
            items = await fetch_offices()
            await crud.upsert_offices(db, items)
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
