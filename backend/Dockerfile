# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 코드 복사
COPY . .

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]