# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 설치 (캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 보안
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
