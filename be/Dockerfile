# be/Dockerfile.cloudtype  ← 빌드 컨텍스트가 'be'일 때 쓰는 버전
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl poppler-utils tesseract-ocr tesseract-ocr-eng tesseract-ocr-kor \
    ghostscript libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 컨텍스트 == be 이므로 경로에 be/ 접두어 붙이지 않음
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 벡터 DB / extracted_rule 포함 전체 복사
COPY . ./

# Cloudtype가 PORT 넣어줌. sh -c로 환경변수 확장
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
