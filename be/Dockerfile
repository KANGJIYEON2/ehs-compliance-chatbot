# be/Dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl poppler-utils tesseract-ocr tesseract-ocr-eng tesseract-ocr-kor \
    ghostscript libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY be/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY be/ ./

# Cloudtype가 $PORT를 세팅해줌 → main.py에서 읽어서 바인딩
CMD ["python", "main.py"]
