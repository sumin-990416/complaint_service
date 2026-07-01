#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
PostgreSQL 데이터베이스와 테이블을 생성합니다.
"""
import asyncio
import logging
from backend.database import init_db
from backend.database import AsyncSessionLocal
from backend import crud
from backend.services.public_api import fetch_offices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """데이터베이스 초기화 및 초기 데이터 로드"""
    try:
        # 1. 테이블 생성
        logger.info("📊 데이터베이스 테이블 생성 중...")
        await init_db()
        logger.info("✅ 테이블 생성 완료")

        # 2. 기존 데이터 확인
        async with AsyncSessionLocal() as db:
            existing = await crud.get_all_offices(db)
            if existing:
                logger.info(f"✅ 기존 데이터 {len(existing)}건 발견")
                return

        # 3. 공공 API에서 민원실 데이터 수집
        logger.info("🔄 공공 API에서 민원실 데이터 수집 중...")
        items = await fetch_offices()
        
        if items:
            async with AsyncSessionLocal() as db:
                await crud.upsert_offices(db, items)
                logger.info(f"✅ 민원실 데이터 {len(items)}건 적재 완료")
        else:
            logger.warning("⚠️  공공 API에서 데이터를 받지 못했습니다")

    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

