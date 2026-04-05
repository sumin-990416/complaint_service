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

## Oracle Cloud(OCI)에서 작업/배포

아래는 Oracle Cloud Ubuntu 인스턴스(예: VM.Standard.E2.1.Micro) 기준으로, 이 저장소를 서버에서 직접 실행하는 절차입니다.

### 1) 인스턴스 준비

Oracle Cloud 콘솔에서 Ubuntu 인스턴스를 생성한 뒤, 보안 목록(Security List) 또는 NSG에서 최소 포트를 열어둡니다.

```text
- 22/tcp: SSH 접속
- 8000/tcp: FastAPI 백엔드
- 5173/tcp: Vite 개발 서버(개발 중에만)
- 80, 443/tcp: (선택) Nginx 리버스 프록시/HTTPS
```

서버 접속:

```bash
ssh -i <your-key>.pem ubuntu@<OCI_PUBLIC_IP>
```

### 2) 필수 패키지 설치

```bash
sudo apt update
sudo apt install -y git curl build-essential python3-venv python3-pip nodejs npm docker.io
sudo usermod -aG docker $USER
```

`docker` 그룹 반영을 위해 한 번 재로그인(또는 새 SSH 세션)을 권장합니다.

### 3) 프로젝트 내려받기

```bash
git clone https://github.com/sumin-990416/complaint_service.git
cd complaint_service
```

### 4) 환경 변수 설정

프로젝트 루트에 `.env` 생성:

```env
service_Key=<공공데이터포털 인증키>
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/complaint_service
openrouter_api_key=<선택: 챗봇 응답 생성 시>
```

프론트엔드 키 설정:

```bash
cat > frontend/.env << 'EOF'
VITE_KAKAO_MAPS_KEY=<카카오 JavaScript 앱 키>
EOF
```

### 5) PostgreSQL 실행(Docker)

```bash
docker run -d --name complaint_pg \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=complaint_service \
  -p 5433:5432 postgres:16
```

이미 있다면:

```bash
docker start complaint_pg
```

### 6) 백엔드 실행

프로젝트 루트에서:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

개발 모드 핫리로드:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 7) 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

접속 주소:

```text
http://<OCI_PUBLIC_IP>:5173
http://<OCI_PUBLIC_IP>:8000/docs
```

### 8) 운영 권장 사항

```text
- 백엔드/프론트를 장기 실행하려면 systemd 또는 pm2 사용
- 실제 서비스는 Nginx로 80/443 종단 + 백엔드(8000) 프록시 권장
- DB는 개발 단계에서는 Docker Postgres, 운영 단계에서는 OCI Managed DB 검토
- 민감 정보(.env, 키 파일)는 Git에 커밋하지 않기
```

### 9) 코드 업데이트(서버에서 최신 반영)

```bash
cd ~/complaint_service
git pull origin main

# 백엔드 의존성 변경 시
source .venv/bin/activate
pip install -e .

# 프론트 변경 시
cd frontend
npm install
```
