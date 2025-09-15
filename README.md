# EHS Compliance Chatbot (KOR) 김안전 비서 🧑‍💼

**법령/규칙 통합 RAG + 별표(OCR/표/그림) 근거 프리뷰 + 깔끔한 프론트(UI)**

> “현장에서 바로 쓰는 EHS 규제 Q\&A.”
> 법·시행령·규칙·별표(표/그림/OCR)를 한 번에 검색하고, **정확한 근거**를 **이미지/표**로 까지 보여줍니다.

---

## ✨ 하이라이트

- **통합 RAG**: 법률·시행령·시행규칙·별표까지 멀티 DB 검색 → 상위 근거 컨텍스트로 LLM 답변
- **별표 프리뷰**: PDF에서 **별표 페이지 이미지** 추출(+OCR 텍스트), **표는 Markdown**으로 미리보기
- **정확성 퍼스트 프롬프트**: “제공 컨텍스트만 사용, 부족하면 부족하다고 명시”
- **근거 토글 UI**: 답변은 깔끔하게, 필요할 때 근거 패널을 열어 이미지/표 확인
- **간편 배포**: Dockerfile 포함. 로컬/Cloudtype/Heroku(컨테이너) 배포 OK
- **윈도우 친화**: Poppler/Tesseract 설치 가이드 & 트러블슈팅 포함

---

## 🧱 아키텍처 개요

```
[User]
  │
  ▼
Frontend (Vite + React + Tailwind + Framer Motion)
  │  └─ /ask 호출 (mode, dbs, topK, ctxChars 등 컨트롤)
  ▼
FastAPI (Python)
  ├─ /ask        : 벡터검색 → 컨텍스트 구성 → LLM 호출 → 답변/근거/이미지URL 반환
  ├─ /health     : DB 로드 상태
  ├─ /reload-db  : 런타임 DB 핫리로드
  └─ /static     : extracted_rule/images/*.png 정적 서빙
      ▲
      │  (PDF 추출 산출물)
  Scripts
  └─ extract_rules_pdf.py : pdfplumber + pdf2image + pytesseract (+ camelot)로
                            별표 텍스트/표/OCR/이미지 추출
      └─ rules_extracted.json, images/*.png, tables/*.md
  │
  ▼
FAISS Vector DB (법령/규칙/별표)
  └─ text-embedding-3-small(1536-d)
```

---

## 📁 폴더 구조

```
ehs-compliance-chatbot/
├─ be/                      # Backend (FastAPI)
│  ├─ main.py               # API (health/ask/reload-db/static)
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ scripts/
│     ├─ extract_rules_pdf.py   # 규칙 PDF → 별표 이미지/OCR/표/텍스트
│     ├─ build_vector_db.py     # laws_meta.json → FAISS 인덱스
│     └─ qa.py                  # CLI 미니 QA
├─ vector_db_law/           # (예) 법령 인덱스 (laws.index, laws_meta.json)
├─ vector_db_rule/          # (예) 규칙/별표 인덱스
└─ extracted_rule/          # PDF 추출 산출물
   ├─ rules_extracted.json
   ├─ images/별표XX_p{page}.png
   └─ tables/별표XX_t{idx}.md
```

---

## ⚙️ 요구 사항

### Backend

- Python 3.11+
- FastAPI, Uvicorn, FAISS, OpenAI SDK(>=1.x), python-dotenv
- pdfplumber, pdf2image, pytesseract, pdfminer.six (표 추출은 camelot-py\[cv] 선택)
- OS 의존 도구

  - **Poppler** (pdf2image용)
  - **Tesseract OCR** (OCR용, `kor`/`eng` 데이터)

### Frontend

- Vite + React
- TailwindCSS
- framer-motion, lucide-react

---

## 🔑 환경 변수 (.env)

`be/.env` (레포에는 절대 커밋하지 마세요)

```env
OPENAI_API_KEY=sk-...
EHS_DB_DIRS=vector_db_law,vector_db_rule
OPENAI_TIMEOUT=90
```

> **보안 팁**
> 커밋 전에 비밀키 유출 검사:
>
> ```bash
> git grep -nI -E "OPENAI_API_KEY|sk-[A-Za-z0-9_-]{20,}" -- .
> ```

---

## 🧪 데이터 파이프라인 (규칙 PDF → 별표 이미지/OCR/표/텍스트)

1. **규칙 PDF 추출**

```bash
# Windows 예시 (Poppler 경로 맞게 수정)
py be/scripts/extract_rules_pdf.py ^
  -i data\rules\산업안전보건기준에_관한_규칙.pdf ^
  -o extracted_rule ^
  --ocr ^
  --poppler-path "C:\Program Files\poppler-25.07.0\Library\bin" ^
  --dpi 300 ^
  --lang "kor+eng"
```

생성물:

- `extracted_rule/rules_extracted.json`
  `type` ∈ {`annex_text`, `annex_ocr`, `table`, `rules_text`}, `image_path` 포함
- `extracted_rule/images/*.png` (별표 페이지 스냅샷)
- `extracted_rule/tables/*.md` (camelot 성공 시)

2. **벡터 DB 빌드**

```bash
# (예) 규칙 DB
py be/scripts/build_vector_db.py -i extracted_rule\rules_extracted.json -o vector_db_rule --law-name "산업안전보건기준에 관한 규칙"

# (예) 법령 DB
py be/scripts/build_vector_db.py -i data\laws\laws_extracted.json -o vector_db_law --law-name "산업안전보건법"
```

---

## ▶️ 백엔드 실행

### 로컬 가상환경

```bash
cd be
python -m venv .venv
. .venv/Scripts/activate          # Windows
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# 또는
python main.py
```

### 엔드포인트

- `GET /health` → `{status, dbs:[{label,size}] }`
- `POST /ask`

  ```json
  {
    "question": "밀폐공간의 정의는?",
    "topk": 5,
    "mode": "auto", // auto|law|rule
    "ctx_chars": 6000,
    "dbs": ["vector_db_law", "vector_db_rule"] // 생략하면 기본 EHS_DB_DIRS
  }
  ```

- `POST /reload-db`:

  ```json
  { "dbs": ["vector_db_law", "vector_db_rule"] }
  ```

- `GET /static/...` 정적 파일 (예: `/static/extracted_rule/images/별표12_p100.png`)

---

## 💻 프론트엔드 실행

`VITE_API_URL`로 백엔드 주소 지정 (미설정 시 `http://127.0.0.1:8000`)

```bash
cd frontend
npm i
npm run dev
```

UI 특징

- **상단 안내 배너**: “이 응답은 보조자료입니다. **최종 판단은 원문 법령 확인**이 필요합니다.”
- **근거 토글**: 기본 닫힘 → 열면 이미지/표 프리뷰 + 근거 리스트
- 모드(auto/law/rule), DB(법률/규칙), TopK, 컨텍스트 길이 조절

---

## 🚀 컨테이너 & 배포

### Docker (로컬)

```bash
cd be
docker build -t ehs-rag-be .
docker run -it --rm -p 8000:8000 --env-file .env ehs-rag-be
# http://127.0.0.1:8000/health
```

### Cloudtype (간단)

- **Dockerfile** 사용
- 포트는 \*\*환경변수 `PORT`\*\*로 주입됨 → `main.py`가 자동 바인딩(`0.0.0.0:PORT`)
- 볼륨/퍼시스턴스 필요 시 `extracted_rule/`, `vector_db_*` 경로 바인딩

### Heroku / Render (Container)

- “Deploy via Dockerfile” 방식 권장
- `OPENAI_API_KEY`, `EHS_DB_DIRS` 환경변수 설정
- 정적 파일은 컨테이너 이미지에 포함되도록 빌드(또는 외부 스토리지)

---

## 🧭 예시 질의 프롬프트

- “**밀폐공간의 정의와 적용 대상**을 알려줘.”
- “**밀폐공간 작업 시 산소농도 기준**과 **환기 요구사항**은?”
- “**사다리 작업대 발판 폭** 최소 기준이 뭐야?”
- “**로스팅 공정 분진 노출 기준**이 별표에 있나?”
- “**크레인 훅 안전장치** 관련 조문 찾아줘. (규칙/별표 우선)”

---

## 🩺 트러블슈팅

### pdf2image: `PDFInfoNotInstalledError`

- **Poppler 미설치/경로** 문제

  - Windows: winget으로 설치 후 PATH에 등록되었는지 확인
  - 또는 `--poppler-path "C:\Program Files\poppler-25.07.0\Library\bin"`

### Tesseract: 한국어 데이터 미검출

- `tesseract --list-langs`에 `kor` 없으면:

  - `kor.traineddata`를 `C:\Program Files\Tesseract-OCR\tessdata` 또는
    `%LOCALAPPDATA%\Tesseract-OCR\tessdata`에 두고
  - 필요 시 `TESSDATA_PREFIX` 환경변수 설정

### Camelot: `No tables found` 경고

- 스캔 PDF/레이아웃 문제일 수 있음

  - **정상**입니다. 실패 페이지는 **건너뜀** (전체 파이프라인 계속 진행)

### 프론트에서 이미지 미표시

- 백엔드 `/static/...` URL 직접 열어 확인

  - 예: `http://127.0.0.1:8000/static/extracted_rule/images/별표12_p100.png`

- CORS 문제 → 백엔드 `CORSMiddleware` 확인(현재 `*` 허용)
- JSON의 `image_url` 필드가 제대로 내려오는지 확인 (`/ask` 응답)

### 응답이 엉뚱하거나 빈약

- `mode="rule"`로 강제하여 규칙/별표 우선
- `topk` ↑, `ctx_chars` ↑
- 벡터 DB(규칙/법령) 최신화/증분 빌드

---

## 🧰 개발 팁

- **스키마 확장**: `hits[].content_format == "markdown"`이면 표로 렌더
- **라벨 표기**: `[법령명 · 조문]` (DB명 표기 제거)
- **성능**: `ctx_chars`로 LLM 토큰 최적화, `topk` 5\~8 추천
- **안전성**: 답변 상단 안내(“보조자료” 문구)로 사용자 기대치 조율

---

## 🗺️ 로드맵(아이디어)

- 🔍 **하이라이트 추출**: 근거 내 핵심 문구 강조
- 📎 **원문 링크 리졸브**: 국가법령정보센터 deep link 매핑
- 🔁 **증분 업데이트**: 관보/개정 추적 후 자동 리빌드
- 👥 **사용자 피드백 루프**: 답변 품질 투표 + 튜닝

---

## 🧾 라이선스

MIT (필요 시 조정)

---

## 🙋‍♂️ 면접 포인트(요약)

- **문서 구조 → 지식 스토어 → 검색 → 근거 중심 생성**의 **엔드 투 엔드 파이프라인**을 스스로 설계/구현
- **OCR/표 처리**로 “텍스트만 있는 RAG”의 한계를 넘어, \*\*별표(숫자/치수/표)\*\*까지 반영
- **근거 토글 UX**로 **정확성·신뢰**와 **가독성**을 동시에 잡음
- **윈도우/도커/클라우드**까지 고려한 실무형 배포 전략

---

> “이 프로젝트의 핵심은 **근거성**입니다.
> 답변만이 아니라 \*\*증거(원문/별표/표)\*\*를 함께 보여 주는 것이 진짜 ‘도움’입니다.”
