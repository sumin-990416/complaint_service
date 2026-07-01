# 배포 체크리스트

## ✅ Railway 백엔드 배포 체크리스트

### 사전 준비
- [ ] Railway 계정 가입: https://railway.app
- [ ] Railway CLI 설치: `npm i -g @railway/cli`
- [ ] GitHub 레포 준비 (public 또는 private)

### 배포 단계

#### 1단계: Railway 프로젝트 생성
```bash
railway login
railway link  # 새 프로젝트 생성 또는 기존 연동
```

#### 2단계: PostgreSQL 추가 (Railway Dashboard)
- Railway Dashboard에서 프로젝트 선택
- "Resources" → "+ Create" → "Database" → "PostgreSQL" 선택
- PostgreSQL 추가됨
- `DATABASE_URL` 환경 변수 자동 생성 확인

#### 3단계: 백엔드 환경 변수 설정
Railway Dashboard → Variables에서 설정:
```
SERVICE_KEY=your_gov_api_key
OPENROUTER_API_KEY=your_openrouter_key
KAKAO_REST_KEY=your_kakao_rest_key (또는 VITE_KAKAO_MAPS_KEY)
FRONTEND_URL=https://your-vercel-frontend.vercel.app (CORS용)
```

#### 4단계: 배포
```bash
railway up
# 또는 GitHub 자동 배포 설정
```

#### 5단계: 확인
- Railway Dashboard에서 "Deployments" 탭 확인
- URL 복사: `https://your-project.up.railway.app`
- API 테스트: `curl https://your-project.up.railway.app/docs`

---

## ✅ Vercel 프론트엔드 배포 체크리스트

### 사전 준비
- [ ] Vercel 계정 가입: https://vercel.com
- [ ] Vercel CLI 설치: `npm i -g vercel`
- [ ] GitHub 레포 준비

### 배포 단계

#### 1단계: Vercel로 프로젝트 배포
```bash
cd frontend
vercel --prod
```

#### 2단계: 프론트엔드 환경 변수 설정
Vercel Dashboard → Settings → Environment Variables에서:
```
VITE_API_URL=https://your-railway-backend.up.railway.app
```

#### 3단계: 자동 배포 활성화 (선택)
- Vercel Dashboard → Git
- GitHub 레포 연동
- 푸시 시 자동 배포

#### 4단계: 확인
- Vercel 대시보드에서 배포 상태 확인
- 프론트엔드 URL 복사
- 브라우저에서 열어서 API 연결 확인

---

## 🔗 통합 테스트

1. **프론트엔드 열기**
   ```
   https://your-vercel-frontend.vercel.app
   ```

2. **Network 탭에서 API 요청 확인**
   - Chrome 개발자 도구 → Network
   - 요청이 `/api/...`로 시작하는지 확인
   - 응답이 정상인지 확인

3. **백엔드 API 직접 확인**
   ```bash
   curl -X GET https://your-railway-backend.up.railway.app/api/offices
   ```

4. **CORS 오류 발생 시**
   - `backend/main.py`의 CORS 설정 확인
   - `allow_origins` 리스트에 Vercel 도메인 추가

---

## 📋 최종 설정 정보

배포 완료 후 정보 정리:

| 항목 | URL/값 |
|------|--------|
| 백엔드 (Railway) | `https://_____.up.railway.app` |
| 프론트엔드 (Vercel) | `https://_____.vercel.app` |
| 데이터베이스 | Railway PostgreSQL (자동) |
| API 문서 | `{백엔드}/docs` |

---

## 🆘 트러블슈팅

### Railway에서 배포 실패
```
Error: Docker build failed
```
**해결:**
- `pyproject.toml` 문법 확인
- `Dockerfile`에서 Python 버전 확인
- Railway 빌드 로그 상세 확인

### Vercel에서 빌드 실패
```
Error: Cannot find module 'vite'
```
**해결:**
- `frontend/package.json` 확인
- `npm install` 실행 후 재배포

### 프론트엔드에서 "API 연결 못함" 오류
```
CORS error / 404 Not Found
```
**해결:**
- `VITE_API_URL` 환경 변수 올바른지 확인
- `backend/main.py`의 CORS origin 확인
- Network 탭에서 실제 요청 URL 확인

### 데이터베이스 연결 오류
```
Error: could not connect to server
```
**해결:**
- Railway Dashboard에서 PostgreSQL 활성화 확인
- `DATABASE_URL` 환경 변수 설정 확인
- `backend/config.py`의 URL 형식 확인: `postgresql+asyncpg://`

---

## 📚 추가 리소스

- [Railway 공식 문서](https://docs.railway.app)
- [Vercel 공식 문서](https://vercel.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL 연결 문자열](https://www.postgresql.org/docs/current/libpq-connect-string.html)
