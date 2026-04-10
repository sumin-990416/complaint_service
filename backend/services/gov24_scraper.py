"""정부24(gov.kr) 민원 서비스 실시간 스크래퍼

robots.txt에서 Allow: /mw/AA020InfoCappView.do 가 명시적으로 허용됨.
서비스 상세 페이지에서 구비서류·처리기간·신청자격 등을 추출한다.
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from html import unescape
from typing import Any

import certifi
import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 키워드 → CappBizCD 정적 매핑
# robots.txt: Allow: /mw/AA020InfoCappView.do 허용됨
# ---------------------------------------------------------------------------
_SERVICE_MAP: dict[str, list[str]] = {
    # 주민등록
    "등본": ["13100000015"],
    "초본": ["13100000015"],
    "등초본": ["13100000015"],
    "주민등록등본": ["13100000015"],
    "주민등록초본": ["13100000015"],
    "주민등록표": ["13100000015"],
    "주민등록열람": ["13100000014"],
    "주민등록정정": ["13100000010"],
    "주민등록재등록": ["13100000011"],
    # 전입신고
    "전입": ["13100000016"],
    "전입신고": ["13100000016"],
    # 인감
    "인감증명": ["13100000025"],
    "인감": ["13100000021", "13100000025"],
    "인감신고": ["13100000021"],
    # 여권
    "여권": ["12600000001"],
    "여권발급": ["12600000001"],
    "여권재발급": ["12600000001"],
    "여권기재사항": ["12600000019"],
    # 운전면허
    "운전면허갱신": ["13200000030"],
    "면허갱신": ["13200000030"],
    "운전면허재발급": ["13200000029"],
    "면허재발급": ["13200000029"],
    "면허증재발급": ["13200000029"],
    "운전면허시험": ["13200000053"],
    "면허시험": ["13200000053"],
    "면허적성검사": ["13200000054"],
    "운전경력증명": ["13200000049"],
    "교통사고확인": ["13200000034"],
    # 토지/부동산
    "토지대장": ["13100000026"],
    "임야대장": ["13100000026"],
    # 지방세/국세
    "납세증명": ["13100000056"],
    "지방세납세증명": ["13100000056"],
    "국세납세증명": ["12100000011"],
    # 병역
    "병적증명": ["13000000016"],
    "병역증": ["13000000007"],
}

# 더 짧은 단어가 여러 서비스로 매핑되는 경우를 위한 최대 서비스 수
_MAX_SERVICES = 2

# CappBizCD → 사람이 읽기 좋은 서비스명
_CODE_NAMES: dict[str, str] = {
    "13100000015": "주민등록등(초)본 발급",
    "13100000014": "주민등록표 열람",
    "13100000010": "주민등록사항 정정",
    "13100000011": "주민등록 재등록",
    "13100000016": "전입신고",
    "13100000025": "인감증명서 발급",
    "13100000021": "인감신고",
    "12600000001": "여권 발급/재발급",
    "12600000019": "여권 기재사항 정정",
    "13200000030": "운전면허 갱신",
    "13200000029": "운전면허증 재발급",
    "13200000053": "운전면허시험 응시",
    "13200000054": "운전면허 적성검사",
    "13200000049": "운전경력증명서 발급",
    "13200000034": "교통사고확인원 발급",
    "13100000026": "토지(임야)대장 발급",
    "13100000056": "지방세 납세증명 발급",
    "12100000011": "국세 납세증명 발급",
    "13000000016": "병적증명서 발급",
    "13000000007": "병역증 발급",
}

_GOV24_BASE = "https://www.gov.kr/mw/AA020InfoCappView.do"

# CappBizCD → 카테고리
_CODE_CATEGORIES: dict[str, str] = {
    "13100000015": "주민등록/등본",
    "13100000014": "주민등록/등본",
    "13100000010": "주민등록/등본",
    "13100000011": "주민등록/등본",
    "13100000016": "전입/가족관계",
    "13100000025": "인감/증명",
    "13100000021": "인감/증명",
    "12600000001": "여권",
    "12600000019": "여권",
    "13200000030": "운전면허",
    "13200000029": "운전면허",
    "13200000053": "운전면허",
    "13200000054": "운전면허",
    "13200000049": "운전면허",
    "13200000034": "운전면허",
    "13100000026": "토지/부동산",
    "13100000056": "세금/납세",
    "12100000011": "세금/납세",
    "13000000016": "병역",
    "13000000007": "병역",
}

# 카테고리별 온라인 신청 가능 여부 (정부24 인터넷 신청 지원 항목)
_CODE_ONLINE_AVAILABLE: set[str] = {
    "13100000015",  # 주민등록등(초)본
    "13100000025",  # 인감증명서
    "13100000026",  # 토지(임야)대장
    "13100000056",  # 지방세 납세증명
    "12100000011",  # 국세 납세증명
    "13000000016",  # 병적증명서
    "13200000049",  # 운전경력증명서
    "13200000034",  # 교통사고확인원
}


def get_full_catalog() -> list[dict[str, str]]:
    """정부24 온라인 신청 가능 민원 전체 카탈로그를 반환."""
    seen: set[str] = set()
    result = []
    for code, name in _CODE_NAMES.items():
        if code in seen:
            continue
        seen.add(code)
        result.append({
            "code": code,
            "label": name,
            "category": _CODE_CATEGORIES.get(code, "기타"),
            "online_available": code in _CODE_ONLINE_AVAILABLE,
            "url": f"{_GOV24_BASE}?CappBizCD={code}",
        })
    return result


def get_gov24_links(query: str) -> list[dict[str, str]]:
    """쿼리에서 키워드를 추출해 정부24 신청 링크 목록을 반환 (HTTP 요청 없음)."""
    query_nospace = re.sub(r"\s+", "", query)

    seen_codes: list[str] = []
    for keyword, codes in _SERVICE_MAP.items():
        if keyword in query or keyword in query_nospace:
            for c in codes:
                if c not in seen_codes:
                    seen_codes.append(c)
        if len(seen_codes) >= 3:
            break

    return [
        {
            "label": _CODE_NAMES.get(code, "민원 신청"),
            "url": f"{_GOV24_BASE}?CappBizCD={code}",
        }
        for code in seen_codes[:3]
    ]

# ---------------------------------------------------------------------------
# TTL 인메모리 캐시
# ---------------------------------------------------------------------------
_cache: dict[str, tuple[float, str]] = {}  # code → (expire_ts, text)
_CACHE_TTL = 3600  # 1시간


def _from_cache(code: str) -> str | None:
    entry = _cache.get(code)
    if entry and time.monotonic() < entry[0]:
        return entry[1]
    _cache.pop(code, None)
    return None


def _to_cache(code: str, text: str) -> None:
    _cache[code] = (time.monotonic() + _CACHE_TTL, text)


# ---------------------------------------------------------------------------
# HTML 파싱
# ---------------------------------------------------------------------------
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; complaint-service-bot/1.0)"}


def _parse_service_page(raw: bytes) -> str:
    """EUC-KR HTML에서 서비스명·신청자격·처리기간·구비서류 텍스트를 추출."""
    html = unescape(raw.decode("euc-kr", errors="replace"))

    # 스크립트/스타일 제거
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", html)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 3]

    result: dict[str, str] = {}

    # --- 서비스명 (타이틀) ---
    m = re.search(r"<title>([^<|]+?)(?:\s*\|)", unescape(raw.decode("euc-kr", errors="replace")))
    if m:
        result["서비스명"] = m.group(1).strip()

    # --- 신청방법 (인터넷/방문/무인발급기) ---
    _METHOD_VALID = {"인터넷", "방문", "무인발급기", "온라인", "우편"}
    for i, line in enumerate(lines):
        if line.strip() == "신청방법":
            methods = lines[i + 1 : i + 6]
            valid = [m for m in methods if m in _METHOD_VALID]
            if valid:
                result["신청방법"] = " / ".join(valid)
            break

    # --- 신청자격 ---
    for i, line in enumerate(lines):
        if line.strip() == "신청자격":
            val = lines[i + 1] if i + 1 < len(lines) else ""
            if val:
                result["신청자격"] = val[:200]
            break

    # --- 처리기간 ---
    for i, line in enumerate(lines):
        if line.strip() == "처리기간":
            for val in lines[i + 1 : i + 5]:
                if val and "이하" not in val and "이상" not in val and "계산" not in val and len(val) < 100:
                    # 열린 괄호로 끝나면 다음 줄 합치기
                    if val.endswith("(") and i + 5 < len(lines):
                        next_val = lines[lines.index(val, i + 1) + 1] if val in lines[i + 1:i + 5] else ""
                        if next_val and len(val + next_val) < 100:
                            val = val + next_val + ")"
                    result["처리기간"] = val.rstrip("(")
                    break
            break

    # --- 수수료 ---
    for i, line in enumerate(lines):
        if "수수료" in line and len(line) < 20:
            val = lines[i + 1] if i + 1 < len(lines) else ""
            if val and len(val) < 200:
                result["수수료"] = val
            break

    # --- 구비서류 (필요서류) ---
    for i, line in enumerate(lines):
        if "같이 제출 해야하는 서류" in line or "민원인이 제출해야" in line:
            # 이후 최대 15줄 수집 (불필요한 버퍼 제거)
            docs: list[str] = []
            for ll in lines[i + 1 : i + 20]:
                if "제출하지 않아도 되는" in ll or "담당공무원" in ll or "행정정보공동" in ll:
                    break
                if ll and ll not in ("민원인이 제출해야하는 서류", "민원인이 제출해야 하는 서류"):
                    docs.append(ll)
            if docs:
                result["구비서류"] = "\n".join(docs[:12])
            break

    if not result:
        return ""

    parts = []
    if "서비스명" in result:
        parts.append(f"[정부24 서비스] {result['서비스명']}")
    if "신청방법" in result:
        parts.append(f"신청방법: {result['신청방법']}")
    if "신청자격" in result:
        parts.append(f"신청자격: {result['신청자격']}")
    if "처리기간" in result:
        parts.append(f"처리기간: {result['처리기간']}")
    if "수수료" in result:
        parts.append(f"수수료: {result['수수료']}")
    if "구비서류" in result:
        parts.append(f"구비서류:\n{result['구비서류']}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

# 동시 요청 제한 (gov24 rate-limit 방어)
_semaphore = asyncio.Semaphore(2)


async def _fetch_one(client: httpx.AsyncClient, code: str) -> str:
    """단일 서비스 페이지를 가져와 텍스트로 변환. 캐시 우선."""
    cached = _from_cache(code)
    if cached is not None:
        return cached

    url = f"https://www.gov.kr/mw/AA020InfoCappView.do?CappBizCD={code}"
    async with _semaphore:
        for attempt in range(2):
            try:
                resp = await client.get(url, headers=_HEADERS, timeout=12)
                if resp.status_code != 200:
                    return ""
                text = _parse_service_page(resp.content)
                if text:
                    _to_cache(code, text)
                return text
            except Exception as exc:
                if attempt == 0:
                    await asyncio.sleep(1)
                else:
                    logger.warning("gov24 fetch failed code=%s: %s", code, exc)
    return ""


async def search_gov24(query: str) -> str:
    """쿼리에서 키워드를 추출하여 정부24 서비스 정보를 반환.

    매칭된 서비스가 없으면 빈 문자열을 반환한다.
    """
    # 공백 없는 버전으로도 매칭 시도 (예: "운전면허 갱신" → "운전면허갱신")
    query_nospace = re.sub(r"\s+", "", query)

    matched_codes: list[str] = []
    for keyword, codes in _SERVICE_MAP.items():
        if keyword in query or keyword in query_nospace:
            for c in codes:
                if c not in matched_codes:
                    matched_codes.append(c)
            if len(matched_codes) >= _MAX_SERVICES:
                break

    if not matched_codes:
        return ""

    async with httpx.AsyncClient(verify=certifi.where()) as client:
        tasks = [_fetch_one(client, code) for code in matched_codes[:_MAX_SERVICES]]
        results = await asyncio.gather(*tasks)

    texts = [r for r in results if r]
    return "\n\n".join(texts)
