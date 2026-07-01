FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN pip install uv

# 프로젝트 파일 복사
COPY pyproject.toml pyproject.toml

# 의존성 설치
RUN uv sync

# 소스코드 복사
COPY backend backend

# 포트 노출
EXPOSE 8000

# 앱 실행
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
