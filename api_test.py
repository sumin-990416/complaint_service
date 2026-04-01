import json
import pprint
from pathlib import Path
from urllib.parse import urlencode

import requests


def load_env(path: str = ".env") -> dict:
    env = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def fetch(service_key: str, endpoint: str = "cso_realtime_v2", stdg_cd: str | None = None) -> dict:
    base_url = f"https://apis.data.go.kr/B551982/cso_v2/{endpoint}"
    params: dict = {"serviceKey": service_key, "type": "json"}
    if stdg_cd:
        params["stdgCd"] = stdg_cd
    url = f"{base_url}?{urlencode(params)}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return json.loads(response.content)


DISTRICT_CODES: dict[str, str] = {
    "광진구청": "1121500000",
    "마포구청": "1144000000",
    "금천구청": "1154500000",
    "영등포구청": "1156000000",
    "서초구청": "1165000000",
    "강동구청": "1174000000",
    "부산광역시청": "2600000000",
    "부산광역시 남구": "2629000000",
    "북구청": "2723000000",
    "수성구청": "2726000000",
    "달서구청": "2729000000",
    "광주광역시청": "2900000000",
    "서구청": "2914000000",
    "남구청": "2915500000",
    "유성구청": "3020000000",
    "세종특별자치시청": "3611000000",
    "수원특례시청": "4111000000",
    "성남시청": "4113000000",
    "의정부시청": "4115000000",
    "부천시청": "4119000000",
    "안산시청": "4127000000",
    "과천시청": "4129000000",
    "군포시청": "4141000000",
    "화성특례시청": "4159000000",
    "광주시청": "4161000000",
    "진천군청": "4375000000",
    "천안시청": "4413000000",
    "보성군청": "4678000000",
    "강진군청": "4681000000",
    "함평군청": "4686000000",
    "영광군청": "4687000000",
    "완도군청": "4689000000",
    "신안군청": "4691000000",
    "구미시청": "4719000000",
    "상주시청": "4725000000",
    "봉화군청": "4792000000",
    "함양군청": "4887000000",
    "제주특별자치도청": "5000000000",
    "철원군청": "5178000000",
    "고성군청": "5182000000",
}


env = load_env()
service_key = env["service_Key"]

print("조회 가능한 지역:")
for name in DISTRICT_CODES:
    print(f"  {name}")

query = input("\n지역 이름을 입력하세요: ").strip()

if query not in DISTRICT_CODES:
    raise SystemExit(f"'{query}'은(는) 목록에 없는 지역입니다.")

code = DISTRICT_CODES[query]
print(f"\n{'='*60}")
print(f"{query} ({code})")
print('='*60)
pprint.pprint(fetch(service_key, stdg_cd=code))
