"""카카오 로컬 REST API 지오코딩 프록시"""
import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.config import settings

router = APIRouter(prefix="/geocode", tags=["geocode"])

KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
KAKAO_ADDRESS_URL = "https://dapi.kakao.com/v2/local/search/address.json"


@router.get("")
async def geocode(q: str = Query(..., description="주소 또는 지역명")):
    """
    카카오 로컬 REST API로 좌표를 반환한다.
    1차: address.json (도로명/지번 주소)
    2차: keyword.json (지역명, 장소명)
    """
    if not settings.kakao_rest_key:
        raise HTTPException(status_code=503, detail="KAKAO_REST_KEY가 설정되지 않았습니다.")

    headers = {"Authorization": f"KakaoAK {settings.kakao_rest_key}"}

    async with httpx.AsyncClient(timeout=8) as client:
        # 1차: 주소 검색
        r = await client.get(KAKAO_ADDRESS_URL, headers=headers, params={"query": q, "size": 1})
        if r.status_code == 200:
            docs = r.json().get("documents", [])
            if docs:
                return {"lat": float(docs[0]["y"]), "lng": float(docs[0]["x"])}

        # 2차: 키워드 검색 (행정구역명, 장소명)
        r = await client.get(KAKAO_KEYWORD_URL, headers=headers, params={"query": q, "size": 1})
        if r.status_code == 200:
            docs = r.json().get("documents", [])
            if docs:
                return {"lat": float(docs[0]["y"]), "lng": float(docs[0]["x"])}

    raise HTTPException(status_code=404, detail="좌표를 찾을 수 없습니다.")
