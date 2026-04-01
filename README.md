# complaint_service
행정안전부 공모전

## 환경 설정

**프로젝트 루트** `.env` (백엔드용):

```env
service_Key=<공공데이터포털 인증키>
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/complaint_service
```

**`frontend/.env`** (프론트엔드용 — Vite는 `frontend/` 디렉터리의 `.env`만 읽습니다):

```env
VITE_KAKAO_MAPS_KEY=<카카오 JavaScript 앱 키>
```

카카오 맵 앱 키는 [카카오 디벨로퍼스](https://developers.kakao.com) > 내 애플리케이션 > 앱 설정 > 앱 키에서 확인합니다.  
플랫폼 > Web > 사이트 도메인에 접속할 URL(로컬: `http://localhost:5173`)을 등록해야 지도가 표시됩니다.

## 실행 방법

### 사전 준비 — PostgreSQL (Docker)

```bash
docker run -d --name complaint_pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=complaint_service \
  -p 5433:5432 postgres:16
```

이미 컨테이너가 있다면:

```bash
docker start complaint_pg
```

### 백엔드 실행

프로젝트 루트(`/workspaces/complaint_service`)에서 실행합니다.

```bash
# 가상환경 활성화
source .venv/bin/activate

# 서버 실행 (포트 8000)
uvicorn backend.main:app --reload --port 8000
```

> `backend/` 디렉터리 안에서 실행하면 모듈을 찾지 못합니다. 반드시 프로젝트 루트에서 실행하세요.

### 프론트엔드 실행

```bash
cd frontend
npm install   # 최초 1회
npm run dev -- --host 0.0.0.0 --port 5173
```

브라우저에서 `http://localhost:5173` 으로 접속합니다.  
GitHub Codespaces 환경이라면 자동 포워딩된 URL로 접속하세요.

## API 테스트 실행

1. 예시 파일을 복사해서 `.env` 생성
2. `DATA_GO_KR_SERVICE_KEY` 값을 본인 키로 입력
3. 실행

```bash
uv run api_test.py
```

엔드포인트를 바꿔 호출할 때:

```bash
uv run api_test.py --endpoint cso_realtime_v2
```

인증키가 `Encoding` 값일 경우:

```bash
uv run api_test.py --service-key-mode encoded
```
