"""민원 안내 챗봇 — OpenRouter API (스트리밍 SSE)"""
import asyncio
from typing import AsyncGenerator

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend import crud
from backend.config import settings
from backend.database import AsyncSessionLocal
from backend.services.gov24_scraper import search_gov24, get_gov24_links, get_full_catalog
from backend.services.rag import search_manual

router = APIRouter(prefix="/chat", tags=["chatbot"])

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-4-maverick"

SYSTEM_PROMPT = """당신은 대한민국 민원실 이용을 도와주는 친절한 AI 도우미입니다.

역할:
- 어떤 민원을 어디서 처리할 수 있는지 안내합니다.
- 사용자가 민원 종류를 말하면 첫 문장에서 반드시 "어느 기관/어느 창구를 먼저 가야 하는지"를 가장 먼저 설명합니다.
- 예: 주민등록/전입/등본/가족관계는 주민센터 또는 구청 민원실, 여권은 여권 민원실 또는 시청/구청 여권 창구, 인허가/건축/개발행위는 시청·구청 담당 부서처럼 우선 접수 기관을 먼저 정리합니다.
- 민원 처리에 필요한 서류, 절차, 운영시간 등을 안내합니다.
- 아래 제공된 민원실 목록 기반으로 가장 적합한 민원실을 추천합니다.
- 접수 기관과 실제 방문 후보를 구분해서 설명합니다.
- 제공된 문서 검색 결과가 있으면 그 내용 안에서 필요서류, 처리절차, 신청방법을 우선 근거로 사용합니다.
- 모르는 내용은 솔직하게 모른다고 답합니다.
- 답변은 간결하고 친절하게 작성하되, 한 문단으로 길게 붙여 쓰지 않습니다.
- 서류, 준비물, 절차, 유의사항이 있으면 반드시 줄바꿈과 리스트 형식을 사용합니다.
- 가능한 경우 아래 형식을 우선 따릅니다.

응답 형식 규칙:
- 첫 줄: 어디를 먼저 가야 하는지 한 문장으로 바로 안내
- 둘째 줄 이후: 필요한 정보는 항목별로 줄바꿈
- 서류/준비물: "- 신분증" 같은 하이픈 리스트 사용
- 절차: "1. 신청서 제출" 같은 번호 리스트 사용
- 주의사항: 별도 줄로 "유의사항:" 다음에 정리
- 문서에 근거가 있으면 추정하지 말고 문서에 있는 내용만 우선 답변
- 줄바꿈 없는 긴 문단, 쉼표로만 이어진 나열식 답변은 금지합니다.
- 반드시 한국어로 답변합니다.

민원 예시: 출생신고, 사망신고, 전입신고, 여권 발급, 주민등록등본, 인감증명서, 건축허가, 사업자등록 등"""


async def _build_offices_context() -> str:
    """DB에서 민원실 목록을 가져와 컨텍스트 문자열로 변환"""
    async with AsyncSessionLocal() as db:
        offices = await crud.get_all_offices(db)
    if not offices:
        return ""
    lines = ["[등록된 민원실 목록]"]
    for o in offices:
        line = f"- {o.cso_nm} ({o.road_nm_addr})"
        if o.wkdy_oper_bgng_tm and o.wkdy_oper_end_tm:
            bgn = o.wkdy_oper_bgng_tm
            end = o.wkdy_oper_end_tm
            line += f" 평일 {bgn[:2]}:{bgn[2:]}~{end[:2]}:{end[2:]}"
        if o.nght_oper_yn == "Y":
            line += " 야간운영"
        if o.wknd_oper_yn == "Y":
            line += " 주말운영"
        lines.append(line)
    return "\n".join(lines)


async def _stream_openrouter(messages: list[dict]) -> AsyncGenerator[str, None]:
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://complaint-service.app",
        "X-Title": "Complaint Service Chatbot",
    }
    payload = {
        "model": MODEL,
        "stream": True,
        "messages": messages,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream("POST", OPENROUTER_URL, headers=headers, json=payload) as resp:
            if resp.status_code != 200:
                body = await resp.aread()
                yield f"data: {{\"error\": \"{resp.status_code}\", \"detail\": {body.decode()}}}\n\n"
                return
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk.strip() == "[DONE]":
                        break
                    yield f"data: {chunk}\n\n"



class ChatRequest(BaseModel):
    messages: list[dict]  # [{"role": "user"/"assistant", "content": "..."}]
    category: str | None = None
    userPos: dict | None = None  # {"lat": float, "lng": float}


@router.get("/gov24-links")
async def gov24_links(q: str = ""):
    """쿼리에 매칭되는 정부24 온라인 신청 링크 목록을 반환 (HTTP 요청 없음)."""
    if not q:
        return []
    return get_gov24_links(q)


@router.get("/gov24-catalog")
async def gov24_catalog():
    """정부24 온라인 신청 민원 전체 카탈로그를 반환."""
    return get_full_catalog()



@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """스트리밍 응답 (SSE)"""
    offices_ctx = await _build_offices_context()
    system_content = SYSTEM_PROMPT
    latest_user_message = next(
        (message.get("content", "") for message in reversed(req.messages) if message.get("role") == "user"),
        "",
    )
    search_query = latest_user_message
    if req.category:
        search_query = f"{req.category} {search_query}".strip()

    manual_chunks, gov24_ctx = await asyncio.gather(
        asyncio.to_thread(search_manual, search_query),
        search_gov24(search_query),
    )

    # 위치 정보 안내 및 프롬프트에 반영
    if req.userPos and isinstance(req.userPos, dict) and 'lat' in req.userPos and 'lng' in req.userPos:
        lat = req.userPos['lat']
        lng = req.userPos['lng']
        system_content += f"\n\n[사용자 위치]\n- 위도: {lat}, 경도: {lng}\n- 반드시 이 위치에서 가까운 민원실을 우선 추천하세요."
    else:
        system_content += "\n\n[위치 정보 없음]\n- 사용자의 위치 정보를 알 수 없습니다. 위치 권한을 안내하거나, 위치 설정 방법을 친절하게 알려주세요."

    if req.category:
        system_content += (
            f"\n\n[선택된 민원 카테고리]\n- {req.category}\n"
            "- 추천이나 안내는 반드시 이 카테고리 범위 안에서만 하세요.\n"
            "- 다른 카테고리의 민원, 다른 성격의 기관, 무관한 추천은 제외하세요.\n"
            "- 답변 첫 부분에 이 카테고리 기준으로 어느 기관을 먼저 가야 하는지 먼저 설명하세요."
        )
    if manual_chunks:
        system_content += "\n\n[민원업무편람 검색 결과]"
        for index, chunk in enumerate(manual_chunks, start=1):
            system_content += f"\n{index}. {chunk}"
    if gov24_ctx:
        system_content += f"\n\n[정부24 실시간 서비스 정보]\n{gov24_ctx}"
    if offices_ctx:
        system_content += f"\n\n{offices_ctx}"

    messages = [{"role": "system", "content": system_content}] + req.messages

    return StreamingResponse(
        _stream_openrouter(messages),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
