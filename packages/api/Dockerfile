# Debian 12 로 고정 — `python:3.11-slim` floating 태그는 예고 없이 OS 가 바뀌어
# (12→13 전환 시 미러 불일치로 apt-get exit 100) 빌드가 비재현적이고 간헐적으로 깨진다.
FROM python:3.11-slim-bookworm AS base

# 일시적 미러 오류에 견디도록 apt 재시도. PDF/OCR(poppler·tesseract·ghostscript) + libgl1.
RUN echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl poppler-utils tesseract-ocr tesseract-ocr-eng tesseract-ocr-kor \
    ghostscript libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Alembic migration + start
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-2}"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1
