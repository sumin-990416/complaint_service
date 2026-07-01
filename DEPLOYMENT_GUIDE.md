# 배포 가이드 (Vercel + Railway)

## 1. Railway 배포 (백엔드)

### 1.1 Railway CLI 설치
```bash
npm i -g @railway/cli
```

### 1.2 Railway 로그인
```bash
railway login
```

### 1.3 프로젝트 생성 및 배포
```bash
cd /workspaces/complaint_service
railway link
railway up
```

### 1.4 환경 변수 설정 (Railway Dashboard)
Railway 대시보드에서 다음 환경 변수를 설정하세요:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
FRONTEND_URL=https://your-vercel-domain.com
```

- `DATABASE_URL`는 Railway가 PostgreSQL 플러그인 추가 시 자동 생성됨

### 1.5 PostgreSQL 플러그인 추가 (Railway Dashboard)
- Resources → Add → PostgreSQL 선택
- 자동으로 `DATABASE_URL` 환경 변수 생성

---

## 2. Vercel 배포 (프론트엔드)

### 2.1 Vercel CLI 설치
```bash
npm i -g vercel
```

### 2.2 Vercel 로그인
```bash
vercel login
```

### 2.3 프로젝트 배포
```bash
cd /workspaces/complaint_service/frontend
vercel
```

### 2.4 환경 변수 설정 (Vercel Dashboard)
Vercel 대시보드에서 다음을 설정하세요:

**Environment Variables:**
```
VITE_API_URL=https://your-railway-backend.up.railway.app
```

### 2.5 vercel.json 설정 확인
이미 `frontend/vercel.json`이 구성되어 있습니다.

---

## 3. 백엔드 환경 변수 참고

`backend/config.py`에서 필요한 환경 변수들:
- `DATABASE_URL`: PostgreSQL 연결 문자열 (Railway에서 자동 제공)
- `FRONTEND_URL`: 프론트엔드 도메인 (CORS 설정용)

---

## 4. 배포 후 확인사항

✅ 백엔드가 정상 작동하는지 확인:
```bash
curl https://your-railway-backend.up.railway.app/docs
```

✅ 프론트엔드에서 API 연결 확인:
- 개발자 도구 → Network 탭에서 API 요청 확인

✅ CORS 오류 확인 및 해결:
- `backend/main.py`의 CORS 설정 검토

---

## 5. 자동 배포 설정 (선택사항)

### GitHub와 연동
- **Railway**: GitHub 레포 연동 → 자동 배포 설정
- **Vercel**: GitHub 레포 연동 → 자동 배포 설정

각 플랫폼 대시보드에서 연동 가능합니다.

---

## 트러블슈팅

### Railway 배포 실패
- `uv pip compile` 단계 확인
- Docker 이미지 빌드 로그 검토

### 프론트엔드에서 백엔드 API 못 찾음
- `VITE_API_URL` 환경 변수 재설정
- CORS 헤더 확인: `frontend/src/api/index.js`

### 데이터베이스 연결 오류
- Railway PostgreSQL 플러그인 활성화 여부 확인
- `DATABASE_URL` 형식 확인
