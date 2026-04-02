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
# 서버 실행 (포트 8000)
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
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

### Codespaces 공유 주의사항

다른 사람이 `app.github.dev` 주소로 접속해야 한다면 다음을 확인해야 합니다.

```text
- 프론트 포트 5173이 0.0.0.0 으로 실행 중인지
- Ports 탭에서 5173 포트 Visibility 가 Public 또는 Organization 인지
- Codespace 가 살아 있는 상태인지
```

예시 URL 형식은 아래와 같습니다.

```text
https://<codespace-name>-5173.app.github.dev
https://<codespace-name>-8000.app.github.dev
```

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

## 문서형 RAG

챗봇은 docs/민원업무편람(2026).hwpx 문서를 직접 읽어 관련 서류, 신청방법, 처리절차를 참고합니다.

동작 방식은 아래와 같습니다.

```text
- HWPX 내부 Preview/PrvText.txt 를 읽어 텍스트 청크를 생성
- 사용자 질문과 카테고리를 기준으로 관련 청크를 검색
- 검색된 문단을 OpenRouter 프롬프트에 함께 전달
```

문서를 교체한 경우에는 백엔드를 다시 실행하면 최신 내용으로 다시 로드됩니다.
