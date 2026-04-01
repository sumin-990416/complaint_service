import math
from urllib.parse import urlencode

import httpx

from backend.config import settings


async def fetch_offices(num_of_rows: int = 100) -> list[dict]:
    url = f"{settings.public_api_base}/cso_info_v2"
    all_items: list[dict] = []

    async with httpx.AsyncClient(timeout=20) as client:
        params = {
            "serviceKey": settings.service_key,
            "type": "json",
            "pageNo": 1,
            "numOfRows": num_of_rows,
        }
        resp = await client.get(f"{url}?{urlencode(params)}")
        resp.raise_for_status()
        data = resp.json()

        total = int(data["body"]["totalCount"])
        total_pages = math.ceil(total / num_of_rows)
        all_items.extend(_extract_items(data))

        for page in range(2, total_pages + 1):
            params["pageNo"] = page
            resp = await client.get(f"{url}?{urlencode(params)}")
            resp.raise_for_status()
            all_items.extend(_extract_items(resp.json()))

    return all_items


async def fetch_realtime(stdg_cd: str | None = None, num_of_rows: int = 100) -> dict:
    url = f"{settings.public_api_base}/cso_realtime_v2"

    async with httpx.AsyncClient(timeout=20) as client:
        params: dict = {
            "serviceKey": settings.service_key,
            "type": "json",
            "numOfRows": num_of_rows,
        }
        if stdg_cd:
            params["stdgCd"] = stdg_cd

        resp = await client.get(f"{url}?{urlencode(params)}")
        resp.raise_for_status()
        data = resp.json()
        body = data.get("body", {})
        items = _extract_items(data)

        return {
            "total_count": int(body.get("totalCount", len(items))),
            "items": items,
        }


def _extract_items(data: dict) -> list[dict]:
    items = data.get("body", {}).get("items", {}).get("item", [])
    if isinstance(items, dict):
        return [items]
    return items or []
