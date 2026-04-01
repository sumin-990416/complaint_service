from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import CsoOffice


async def get_all_offices(db: AsyncSession) -> list[CsoOffice]:
    result = await db.execute(select(CsoOffice).order_by(CsoOffice.cso_nm))
    return list(result.scalars().all())


async def get_office_by_sn(db: AsyncSession, cso_sn: str) -> CsoOffice | None:
    result = await db.execute(select(CsoOffice).where(CsoOffice.cso_sn == cso_sn))
    return result.scalar_one_or_none()


async def get_offices_by_stdg_cd(db: AsyncSession, stdg_cd: str) -> list[CsoOffice]:
    result = await db.execute(
        select(CsoOffice).where(CsoOffice.stdg_cd == stdg_cd)
    )
    return list(result.scalars().all())


async def upsert_offices(db: AsyncSession, offices: list[dict]) -> int:
    from datetime import datetime

    for item in offices:
        existing = await get_office_by_sn(db, item["csoSn"])
        if existing:
            for key, value in _map_fields(item).items():
                setattr(existing, key, value)
            existing.updated_at = datetime.now()
        else:
            db.add(CsoOffice(**_map_fields(item), updated_at=datetime.now()))

    await db.commit()
    return len(offices)


def _map_fields(item: dict) -> dict:
    return {
        "cso_sn": item.get("csoSn"),
        "stdg_cd": item.get("stdgCd"),
        "cso_nm": item.get("csoNm"),
        "lotno_addr": item.get("lotnoAddr"),
        "road_nm_addr": item.get("roadNmAddr"),
        "lat": _to_float(item.get("lat")),
        "lot": _to_float(item.get("lot")),
        "wkdy_oper_bgng_tm": item.get("wkdyOperBgngTm"),
        "wkdy_oper_end_tm": item.get("wkdyOperEndTm"),
        "nght_oper_yn": item.get("nghtOperYn"),
        "nght_dow_expln": item.get("nghtDowExpln"),
        "wknd_oper_yn": item.get("wkndOperYn"),
        "wknd_dow_expln": item.get("wkndDowExpln"),
        "tot_crtr_ymd": item.get("totCrtrYmd"),
    }


def _to_float(value) -> float | None:
    try:
        return float(value) if value else None
    except (ValueError, TypeError):
        return None
