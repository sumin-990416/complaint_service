from fastapi import APIRouter, Query

from backend.schemas import RealtimeResponse
from backend.services import public_api

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("", response_model=RealtimeResponse)
async def get_realtime(
    stdg_cd: str | None = Query(default=None, description="법정동 코드 (없으면 전체 조회)")
):
    data = await public_api.fetch_realtime(stdg_cd=stdg_cd)
    items = [
        {
            "cso_sn": it.get("csoSn", ""),
            "cso_nm": it.get("csoNm", ""),
            "stdg_cd": it.get("stdgCd", ""),
            "task_no": it.get("taskNo", ""),
            "task_nm": it.get("taskNm", ""),
            "clot_no": it.get("clotNo", ""),
            "clot_cnter_no": it.get("clotCnterNo", ""),
            "wtng_cnt": it.get("wtngCnt", "0"),
            "tot_dt": it.get("totDt", ""),
        }
        for it in data["items"]
    ]
    return RealtimeResponse(
        stdg_cd=stdg_cd,
        total_count=data["total_count"],
        items=items,
    )
