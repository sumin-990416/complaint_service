from __future__ import annotations

import re
from html import unescape
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zipfile import ZipFile


DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "민원업무편람(2026).hwpx"
PREVIEW_PATH = "Preview/PrvText.txt"
SECTION_XML_PATH = "Contents/section0.xml"
QUERY_SYNONYMS = {
    "주민등록등본": ["주민등록 등초본", "주민등록 등 초본", "등초본"],
    "주민등록초본": ["주민등록 등초본", "주민등록 등 초본", "등초본"],
    "등본": ["등초본", "주민등록 등초본"],
    "초본": ["등초본", "주민등록 등초본"],
    "출생신고": ["출생신고 절차"],
    "사망신고": ["사망신고 절차"],
    "혼인신고": ["혼인신고 절차"],
    "이혼신고": ["이혼신고 절차"],
    "개명신고": ["개명신고 절차"],
    "여권재발급": ["여권발급", "온라인 여권 재발급신청"],
    "여권발급": ["여권발급 기본사항"],
}


@dataclass(slots=True)
class RagChunk:
    text: str
    tokens: set[str]


def _normalize_text(text: str) -> str:
    text = text.replace("<", " ").replace(">", " ")
    text = text.replace("\u200b", " ")
    text = re.sub(r"[□○☞▶※]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _compact_text(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[가-힣A-Za-z0-9]+", text.lower())
        if len(token) >= 2
    }


def _expand_query(query_text: str) -> list[str]:
    expanded = [query_text]
    compact_query = _compact_text(query_text)
    for key, values in QUERY_SYNONYMS.items():
        if key in compact_query:
            expanded.extend(values)
    return expanded


def _load_hwpx_preview_text() -> str:
    if not DOC_PATH.exists():
        return ""

    with ZipFile(DOC_PATH) as archive:
        with archive.open(PREVIEW_PATH) as preview:
            return preview.read().decode("utf-8", errors="ignore")


def _load_hwpx_section_xml() -> str:
    if not DOC_PATH.exists():
        return ""

    with ZipFile(DOC_PATH) as archive:
        with archive.open(SECTION_XML_PATH) as section:
            return section.read().decode("utf-8", errors="ignore")


def _split_long_text(text: str, chunk_size: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    pieces: list[str] = []
    start = 0
    overlap = 120
    while start < len(text):
        end = min(start + chunk_size, len(text))
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [piece for piece in pieces if piece]


def _build_chunks(raw_text: str, chunk_size: int = 700) -> list[RagChunk]:
    raw_text = re.sub(r">\s*<", ">\n<", raw_text)
    cleaned_lines = []
    for raw_line in raw_text.splitlines():
        line = _normalize_text(raw_line)
        if len(line) < 3:
            continue
        cleaned_lines.extend(_split_long_text(line, chunk_size))

    merged_text = "\n".join(cleaned_lines)
    chunks = _split_long_text(merged_text, chunk_size)
    return [RagChunk(text=chunk, tokens=_tokenize(chunk)) for chunk in chunks]


def _extract_paragraphs_from_section_xml(raw_xml: str) -> list[str]:
    paragraphs: list[str] = []
    for paragraph_xml in re.findall(r"<hp:p\b.*?</hp:p>", raw_xml, flags=re.DOTALL):
        texts = re.findall(r"<hp:t>(.*?)</hp:t>", paragraph_xml, flags=re.DOTALL)
        if not texts:
            continue
        paragraph = _normalize_text(unescape(" ".join(texts)))
        if len(paragraph) >= 3:
            paragraphs.append(paragraph)
    return paragraphs


def _build_chunks_from_paragraphs(paragraphs: list[str], chunk_size: int = 650) -> list[RagChunk]:
    chunks: list[RagChunk] = []
    buffer: list[str] = []
    length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)
        if buffer and length + paragraph_length > chunk_size:
            text = "\n".join(buffer)
            chunks.append(RagChunk(text=text, tokens=_tokenize(text)))
            overlap = buffer[-2:] if len(buffer) > 2 else buffer[-1:]
            buffer = overlap.copy()
            length = sum(len(item) for item in buffer)

        buffer.append(paragraph)
        length += paragraph_length

    if buffer:
        text = "\n".join(buffer)
        chunks.append(RagChunk(text=text, tokens=_tokenize(text)))

    return chunks


@lru_cache(maxsize=1)
def get_rag_chunks() -> list[RagChunk]:
    raw_xml = _load_hwpx_section_xml()
    if raw_xml:
        paragraphs = _extract_paragraphs_from_section_xml(raw_xml)
        if paragraphs:
            return _build_chunks_from_paragraphs(paragraphs, chunk_size=650)

    raw_text = _load_hwpx_preview_text()
    if not raw_text:
        return []
    return _build_chunks(raw_text, chunk_size=450)


def search_manual(query: str, *, top_k: int = 4) -> list[str]:
    query_text = _normalize_text(query)
    if not query_text:
        return []

    expanded_queries = _expand_query(query_text)
    query_tokens = set()
    compact_queries = []
    for item in expanded_queries:
        query_tokens.update(_tokenize(item))
        compact_queries.append(_compact_text(item))
    if not query_tokens:
        return []

    scored: list[tuple[float, str]] = []
    for chunk in get_rag_chunks():
        overlap = len(query_tokens & chunk.tokens)
        compact_chunk = _compact_text(chunk.text)
        if overlap == 0 and not any(compact_query in compact_chunk for compact_query in compact_queries):
            continue

        score = float(overlap)
        if any(item.lower() in chunk.text.lower() for item in expanded_queries):
            score += 3.0
        if any(compact_query and compact_query in compact_chunk for compact_query in compact_queries):
            score += 2.5
        if any(token in chunk.text.lower() for token in query_tokens):
            score += 0.5
        if any(keyword in query_text for keyword in ("필요서류", "신청방법", "처리절차")):
            if "필요서류" in chunk.text:
                score += 2.0
            if "신청방법" in chunk.text:
                score += 2.0
            if "처리절차" in chunk.text:
                score += 2.0
        if any(keyword in chunk.text for keyword in ("목 차", "차 례", "목차")):
            score -= 3.0

        scored.append((score, chunk.text))

    scored.sort(key=lambda item: item[0], reverse=True)

    non_toc = [item for item in scored if not any(keyword in item[1] for keyword in ("목 차", "차 례", "목차"))]
    if non_toc:
        scored = non_toc + [item for item in scored if item not in non_toc]

    results: list[str] = []
    seen = set()
    for _, text in scored:
        if text in seen:
            continue
        seen.add(text)
        results.append(text)
        if len(results) >= top_k:
            break
    return results