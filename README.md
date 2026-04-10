# 민원실 이용현황 서비스

> 행정안전부 공공데이터 활용 공모전 출품작

---

## 서비스 소개

### 배경 및 문제 인식

대한민국 전역에는 3,000개 이상의 행정 민원실이 운영되고 있습니다. 그러나 많은 국민이 민원실을 방문하기 전 다음과 같은 불편을 겪고 있습니다.

- **헛걸음 문제**: 현장 대기가 길어 업무를 처리하지 못하고 돌아오는 경우가 빈번합니다.
- **정보 부재**: 어떤 민원실에서 어떤 서류로 어떤 업무를 처리할 수 있는지 사전에 파악하기 어렵습니다.
- **접근성 한계**: 고령층·디지털 취약계층은 복잡한 민원 절차를 혼자 이해하고 준비하는 데 어려움을 겪습니다.

### 서비스 목적

본 서비스는 **행정안전부 공공 민원실 데이터**를 바탕으로, 국민이 민원실 방문 전에 충분한 정보를 갖추고 효율적으로 이용할 수 있도록 지원합니다.

1. **실시간 대기현황 제공**: 지금 이 순간 어느 민원실이 얼마나 붐비는지 즉시 확인
2. **AI 혼잡도 예측**: 과거 대기 데이터를 학습한 ML 모델로 원하는 시간대의 예상 혼잡도 안내
3. **AI 챗봇 상담**: 민원업무편람과 정부24 정보를 실시간으로 참조해 필요 서류·절차를 자연어로 안내
4. **지도 기반 탐색**: 현위치 또는 주소 검색으로 주변 민원실을 지도에서 바로 찾기

### 기대 효과

| 대상 | 기대 효과 |
|---|---|
| 방문 국민 | 헛걸음 감소, 민원 처리 소요 시간 단축 |
| 민원 취약계층 | AI 챗봇을 통한 절차·서류 간편 안내 |
| 민원실 운영자 | 혼잡 시간대 분산 유도로 운영 효율 향상 |
| 행정기관 | 공공 데이터 활용 가치 제고 |

### 활용 공공 데이터

- **행정안전부 민원실 정보 및 실시간 대기현황 API** (`apis.data.go.kr/B551982/cso_v2`)
- **민원업무편람(2026)**: 민원별 구비서류, 처리기간, 신청방법 수록 공식 자료집
- **정부24 민원 서비스 정보**: 개별 민원 상세정보 (구비서류, 신청자격 등)

---

## 기술 스택

| 영역 | 기술 |
|---|---|
| 백엔드 | FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, APScheduler |
| 머신러닝 | scikit-learn (Gradient Boosting), joblib |
| AI 챗봇 | OpenRouter API (Llama 4 Maverick), RAG |
| 프론트엔드 | Vue 3, Vite, Tailwind CSS, 카카오 Maps JS SDK |

---

## 기존 서비스와의 차별성 및 독창성

### 유사 서비스 비교

| 기능 | 정부24 | 네이버/카카오 지도 | 본 서비스 |
|---|:---:|:---:|:---:|
| 민원실 위치 검색 | △ | ✅ | ✅ |
| **실시간 현장 대기인원 조회** | ❌ | ❌ | ✅ |
| **시간대별 혼잡도 AI 예측** | ❌ | ❌ | ✅ |
| **자연어 민원 절차 상담** | ❌ | ❌ | ✅ |
| 현위치 반경 내 기관 탐색 | ❌ | ✅ | ✅ |
| **정부24 온라인 신청 바로가기 연동** | — | ❌ | ✅ |

### 차별화 포인트

#### 1. 공공 API를 활용한 실시간 대기현황 — 업계 유일 통합 제공
정부24는 온라인 민원 신청 플랫폼이며 **현장 대기 정보를 제공하지 않습니다.** 네이버·카카오 지도는 위치 및 영업 정보만 표시할 뿐 혼잡 수준을 알 수 없습니다. 본 서비스는 행정안전부 공공 API를 5분 주기로 수집해 국민에게 **현재 시각 기준 정확한 창구별 대기 인원**을 제공하는 최초의 통합 서비스입니다.

#### 2. ML 기반 방문 시간대 예측 — 데이터 기반 의사결정 지원
단순 조회를 넘어 누적 대기 스냅샷 데이터를 **Gradient Boosting 모델**로 학습해 "내일 오전 9시에 가면 얼마나 기다려야 하는가"를 사전에 알려줍니다. 매일 자정 자동 재학습으로 데이터가 쌓일수록 정확도가 높아지는 **자기 개선형 구조**를 채택했습니다.

#### 3. 공식 문서 기반 RAG 챗봇 — 환각 최소화 정확 안내
일반 LLM 챗봇과 달리 **민원업무편람(2026) 원문**과 **정부24 실시간 스크래핑** 데이터를 근거로 답변합니다. 질문과 관련된 청크만 선별해 프롬프트에 주입하는 RAG 방식을 적용해 **구비서류, 처리기간, 수수료**를 공식 출처에 근거해 안내하므로 AI 환각(Hallucination) 위험이 현저히 낮습니다.

#### 4. 온·오프라인 연계 — 정부24 신청 바로가기
민원 안내에서 그치지 않고, 챗봇 답변과 민원실 상세 화면에서 **해당 민원의 정부24 온라인 신청 페이지로 직접 이동**할 수 있는 링크를 자동 제공합니다. 방문이 필요 없는 민원은 온라인으로 즉시 처리할 수 있는 경로를 함께 안내해 **오프라인 방문 수요 자체를 줄이는** 선택지를 제공합니다.

#### 5. 취약계층을 배려한 자연어 인터페이스
복잡한 메뉴·검색 없이 "여권 발급하려면 어떤 서류가 필요해요?" 같은 일상 언어로 질문하면 절차·서류·담당 기관까지 한 번에 정리해줍니다. 정보 접근성이 낮은 **고령층·디지털 취약계층**의 민원 이용 장벽을 낮추는 것이 핵심 가치입니다.

---

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
