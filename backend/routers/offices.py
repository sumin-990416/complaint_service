from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend import crud
from backend.database import get_db
from backend.schemas import CsoOfficeResponse
from backend.services import public_api

router = APIRouter(prefix="/offices", tags=["offices"])


@router.get("", response_model=list[CsoOfficeResponse])
async def list_offices(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_offices(db)


@router.post("/sync", response_model=dict)
async def sync_offices(db: AsyncSession = Depends(get_db)):
    items = await public_api.fetch_offices()
    count = await crud.upsert_offices(db, items)
    return {"synced": count}


@router.get("/{cso_sn}", response_model=CsoOfficeResponse)
async def get_office(cso_sn: str, db: AsyncSession = Depends(get_db)):
    office = await crud.get_office_by_sn(db, cso_sn)
    if not office:
        raise HTTPException(status_code=404, detail="민원실을 찾을 수 없습니다.")
    return office
