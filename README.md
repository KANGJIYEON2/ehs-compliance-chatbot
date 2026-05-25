<p align="center">
  <img src="https://img.shields.io/badge/SafetyAI-EHS%20Platform-0066FF?style=for-the-badge&logo=shield&logoColor=white" alt="SafetyAI" />
</p>

<h1 align="center">SafetyAI — 기업형 EHS 리스크 관리 플랫폼</h1>

<p align="center">
  AI 기반 산업안전보건(EHS) 관리 SaaS — 관리자-작업자 듀얼 트랙 아키텍처<br/>
  <strong>관리자 웹 대시보드</strong> (18페이지) + <strong>작업자 모바일 PWA</strong> (9페이지)
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI_GPT--4o-412991?style=flat-square&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />
</p>

<p align="center">
  <a href="https://safety-ai.team-ieum.com">라이브 데모</a> &middot;
  <a href="#빠른-시작">빠른 시작</a> &middot;
  <a href="#api-레퍼런스">API 레퍼런스</a> &middot;
  <a href="#아키텍처">아키텍처</a>
</p>

---

## 만들게 된 이유

한국의 산업 현장은 심각한 안전 과제에 직면해 있습니다. 2022년 한 해에만 산업재해로 **2,000명 이상의 근로자가 사망**했습니다. **중대재해처벌법**은 안전 조치 실패에 대해 경영책임자에게 형사 책임을 부과하지만, 여전히 대부분의 중소 제조업체는 종이 체크리스트와 엑셀로 안전을 관리하고 있습니다.

이 플랫폼을 만든 이유:

1. **종이 기반 안전관리 탈피** — 사고 보고, TBM 회의, 위험성평가를 디지털화
2. **안전팀을 위한 실용적 AI** — 단순 챗봇이 아닌, 근본 원인을 분석하고 위험을 예측하며 법적 근거 체크리스트를 자동 생성하는 내장형 AI
3. **언어 장벽 해소** — 외국인 근로자(베트남, 캄보디아, 네팔, 미얀마, 영어)가 QR코드로 모국어 안전수칙을 확인
4. **관리자뿐 아니라 작업자도** — 익명 제보, 음성 기반 사고 접수, 게이미피케이션으로 안전 행동 유도

처음에는 RAG 기반 법령 검색 챗봇으로 시작했지만, 법률 검색만으로는 생명을 구할 수 없다는 것을 깨닫고 **선제적 리스크 관리 플랫폼**으로 발전시켰습니다.

---

## 라이브 데모

> **https://safety-ai.team-ieum.com**

| 역할 | 이메일 | 비밀번호 | 접근 범위 |
|------|--------|----------|-----------|
| 슈퍼관리자 | `superadmin@safetyai.kr` | `super123` | 플랫폼 전체 관리 |
| 관리자 | `admin@hankook-steel.kr` | `admin123` | 회사 전체 접근 (관리자 대시보드) |
| 현장담당자 | `park.jm@hankook-steel.kr` | `field123` | 배정된 사업장만 |
| 작업자 | `kim.worker@hankook-steel.kr` | `worker123` | 작업자 PWA (`/worker/`) |

**관리자 대시보드:** https://safety-ai.team-ieum.com
**작업자 PWA:** https://safety-ai.team-ieum.com/worker/

---

## 주요 기능

### 관리자 트랙 (웹 대시보드 — 18페이지)

| 기능 | 설명 |
|------|------|
| **사고/아차사고 관리** | 9개 유형, 4단계 심각도, 상태 워크플로우 (접수 → 조치중 → 완료 → 재발관리), 담당자 배정 + 기한 관리 |
| **AI 원인 분석** | GPT-4o가 사고 분석 → 근본 원인, 기여 요인, 예방 체크리스트, 법적 근거 자동 생성 |
| **법령 컴플라이언스 (RAG)** | FAISS 벡터 검색 (14,500+ 법령/규칙 엔트리) + 국가법령정보센터 API → 관련 법조문, 사업주 의무, 벌칙 |
| **대시보드 & 분석** | KPI 카드, 추이 차트 (Recharts), AI 인사이트, 기한 초과 경고 |
| **월간 PDF 리포트** | 유형별/심각도별/상태별 통계 + AI 요약이 포함된 자동 생성 보고서 |
| **TBM 디지털화** | AI가 작업 전 안전회의 안건 자동 생성, 참석자 관리 |
| **위험성평가** | AI가 유해위험요인 식별 → 위험도 매트릭스 → 감소대책 → 법적 요건 분석 |
| **익명 제보 관리** | 작업자가 신원 노출 없이 제보 → AI 위험등급 분류 → 관리자 피드백 |
| **다국어 안전수칙** | 한국어 작성 → GPT 5개 국어 번역 → QR코드 생성 → 교육 이수 확인 |
| **게이미피케이션** | 포인트, 팀 랭킹, AI 일일 퀴즈, 위험 예측 점수 |
| **알림 시스템** | 사고 배정, 기한 초과, 신규 제보 실시간 알림 |

### 작업자 트랙 (모바일 PWA — 9페이지)

| 기능 | 설명 |
|------|------|
| **음성 보고** | 말하기 → Whisper STT → GPT 구조화 파싱 → 사고 자동 등록 |
| **익명 제보** | 신원 비저장, 토큰 기반 결과 확인 |
| **안전 퀴즈** | AI가 매일 새 문제 생성, 정답 시 +20 포인트 |
| **팀 랭킹** | 게이미피케이션 기반 안전 경쟁, 메달 표시 |
| **안전수칙 조회** | QR 스캔 → 다국어 안전수칙 → 교육 이수 확인 |
| **위험 예측** | 사업장 공정별 위험도 스코어 시각화 |
| **마이페이지** | 포인트 현황, 활동 내역, 개인 랭킹 |

---

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx 리버스 프록시                        │
│   /           → 관리자 React 앱                               │
│   /worker/    → 작업자 React PWA                              │
│   /api/       → FastAPI 백엔드                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐   ┌────────────────────────────┐  │
│  │   관리자 대시보드       │   │    작업자 PWA (모바일)      │  │
│  │   React 19 + Vite 7   │   │    React 19 + Vite 7      │  │
│  │   18 페이지            │   │    9 페이지                │  │
│  │   TailwindCSS 4       │   │    하단 내비 + 다크 테마    │  │
│  └──────────┬───────────┘   └──────────────┬─────────────┘  │
│             │                               │                │
│             └───────────────┬───────────────┘                │
│                             ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI 백엔드 (Python 3.11)              │   │
│  │   50+ REST 엔드포인트 · JWT 4단계 권한 · SQLAlchemy    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                   AI 에이전트 레이어                    │   │
│  │  ┌──────────┬────────────┬──────────┬─────────────┐  │   │
│  │  │NewsAgent │IncidentAg  │ LawAgent │ VoiceAgent  │  │   │
│  │  │RSS+GPT   │원인분석     │ RAG+법령 │ Whisper+GPT │  │   │
│  │  └──────────┴────────────┴──────────┴─────────────┘  │   │
│  │         BaseAgent (공유 OpenAI 클라이언트)              │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  FAISS 벡터 DB            PostgreSQL 16               │   │
│  │  법률 784건 + 규칙 13,802건  22개 테이블               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 기술 스택

| 영역 | 기술 |
|------|------|
| **백엔드** | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, JWT (python-jose + bcrypt) |
| **AI/ML** | OpenAI GPT-4o-mini, Whisper-1, text-embedding-3-small, FAISS |
| **프론트엔드** | React 19, TypeScript, Vite 7, TailwindCSS 4, Zustand, Recharts, Framer Motion |
| **데이터베이스** | PostgreSQL 16 (운영) / SQLite (개발), 22개 테이블 |
| **PDF** | pdfplumber + pytesseract (추출), ReportLab (생성) |
| **인프라** | Docker, docker-compose, Nginx, AWS EC2 |

### 데이터베이스 스키마 (22개 테이블)

```
companies ─┬─ sites ─┬─ departments
            │         ├─ processes ──── equipment
            │         ├─ work_zones
            │         ├─ incidents ──── incident_attachments
            │         │                 ai_analysis_results
            │         ├─ anonymous_reports
            │         ├─ safety_guides ─── translations
            │         │                    training_records
            │         ├─ tbm_sessions ──── tbm_attendees
            │         ├─ risk_assessments
            │         ├─ safety_quizzes ── quiz_responses
            │         ├─ risk_scores
            │         └─ safety_points
            │
            └─ users ──── notifications
```

---

## 빠른 시작

### 방법 1: Docker (권장)

```bash
# 클론
git clone https://github.com/your-username/ehs-compliance-chatbot.git
cd ehs-compliance-chatbot

# 환경 변수 설정
cp .env.example .env
# .env 편집: JWT_SECRET_KEY, OPENAI_API_KEY 설정

# 전체 서비스 실행
docker-compose up --build

# 데모 데이터 투입 (다른 터미널에서)
docker-compose exec api python scripts/seed_demo_data.py

# 접속
# 관리자:  http://localhost
# 작업자:  http://localhost/worker/
# API:     http://localhost/api/docs
```

### 방법 2: 로컬 개발

```bash
# 1. 백엔드
cd packages/api
pip install -r requirements.txt
cp .env.example .env  # API 키 등 설정
alembic upgrade head
python scripts/seed_demo_data.py  # 데모 데이터 투입
uvicorn app.main:app --reload --port 8000

# 2. 관리자 프론트엔드 (새 터미널)
cd apps/admin
npm install
npm run dev  # → http://localhost:3000

# 3. 작업자 프론트엔드 (새 터미널)
cd apps/worker
npm install
npm run dev  # → http://localhost:3001
```

### 환경 변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `JWT_SECRET_KEY` | O | JWT 서명용 랜덤 시크릿 (최소 32자) |
| `OPENAI_API_KEY` | O | OpenAI API 키 (AI 기능 사용) |
| `EHS_DATABASE_URL` | X | DB URL (기본값: `sqlite:///./ehs.db`) |
| `LAW_API_KEY` | X | 국가법령정보센터 API 키 |
| `CORS_ORIGINS` | X | 허용 오리진 (기본값: `*`) |
| `DB_PASSWORD` | X | PostgreSQL 비밀번호 (Docker 전용) |

---

## API 레퍼런스

플랫폼은 19개 라우트 그룹에 걸쳐 **50개 이상의 REST 엔드포인트**를 제공합니다.

<details>
<summary><strong>인증 & 사용자</strong></summary>

```
POST /api/auth/register        # 회사 등록 (회사 + 관리자 생성)
POST /api/auth/login           # JWT 토큰 발급 (access + refresh)
POST /api/auth/refresh         # 토큰 갱신
GET  /api/auth/me              # 현재 사용자 프로필
POST /api/auth/users           # 관리자가 사용자 생성 (현장담당자/작업자)
```
</details>

<details>
<summary><strong>사업장 & 마스터데이터</strong></summary>

```
CRUD /api/sites                          # 사업장 관리
CRUD /api/sites/:id/departments          # 부서
CRUD /api/sites/:id/processes            # 생산 공정
CRUD /api/sites/:id/equipment            # 설비
CRUD /api/sites/:id/work-zones           # 작업 구역
```
</details>

<details>
<summary><strong>사고/아차사고</strong></summary>

```
GET  /api/incidents            # 목록 (필터/페이징: 유형, 심각도, 상태, 날짜)
POST /api/incidents            # 사고 등록
GET  /api/incidents/:id        # 상세 조회
PATCH /api/incidents/:id       # 수정 (상태, 담당자, 기한)
DELETE /api/incidents/:id      # 삭제
POST /api/incidents/:id/files  # 첨부파일 업로드 (스트리밍, 10MB 제한)
DELETE /api/incidents/:id/files/:fid  # 첨부파일 삭제
```
</details>

<details>
<summary><strong>AI 분석 (24시간 캐싱)</strong></summary>

```
GET  /api/ai/incidents/:id/results    # 저장된 분석 결과 전체 조회
POST /api/ai/incidents/:id/analyze    # 근본 원인 + 위험 수준 + 기여 요인
POST /api/ai/incidents/:id/checklist  # 예방 체크리스트 생성
POST /api/ai/incidents/:id/legal      # 관련 법령 + 벌칙 + 사업주 의무
POST /api/ai/legal-basis              # 일반 법령 검색 (사고 비종속)
```
</details>

<details>
<summary><strong>분석 & 리포트</strong></summary>

```
GET /api/analytics/summary     # 총 건수 + 상태별 + 심각도별
GET /api/analytics/by-type     # 사고 유형별 분포
GET /api/analytics/by-month    # 월별 추이 (12개월)
GET /api/analytics/by-status   # 상태별 분포
GET /api/analytics/insights    # AI 인사이트 (추세, 패턴, 위험)
GET /api/reports/monthly       # PDF 리포트 다운로드
```
</details>

<details>
<summary><strong>음성 보고</strong></summary>

```
POST /api/voice/transcribe     # 오디오 → 텍스트 (Whisper STT)
POST /api/voice/parse          # 텍스트 → 구조화된 사고 데이터 (GPT)
POST /api/voice/submit         # 파싱 데이터 → 사고 등록
```
</details>

<details>
<summary><strong>익명 제보</strong></summary>

```
POST  /api/anonymous-reports              # 제보 접수 (인증 불필요)
GET   /api/anonymous-reports/check/:token # 토큰으로 상태 확인
GET   /api/anonymous-reports/admin        # 관리자: 제보 목록
PATCH /api/anonymous-reports/admin/:id    # 관리자: 응답/해결
```
</details>

<details>
<summary><strong>TBM, 위험성평가, 안전수칙, 게이미피케이션, 알림</strong></summary>

```
# TBM (작업 전 안전회의)
POST /api/tbm                  # 세션 생성 (AI 안건 자동 생성)
GET  /api/tbm                  # 세션 목록
GET  /api/tbm/:id              # 상세 (참석자 포함)
POST /api/tbm/:id/attend       # 참석 기록

# 위험성평가
POST  /api/risk-assessment              # AI 분석 (유해요인/매트릭스/대책/법령)
GET   /api/risk-assessment              # 평가 목록
GET   /api/risk-assessment/:id          # 상세
PATCH /api/risk-assessment/:id/status   # 상태 변경

# 안전수칙 (다국어)
POST /api/safety-guide                 # 가이드 작성 (한국어)
GET  /api/safety-guide/list            # 목록
POST /api/safety-guide/:id/translate   # GPT 번역 (vi/en/km/ne/my)
GET  /api/safety-guide/qr/:id         # QR코드 PNG
GET  /api/safety-guide/:id            # 공개 조회 (인증 불필요, QR 스캔용)
POST /api/safety-guide/:id/ack        # 교육 이수 확인

# 게이미피케이션
GET  /api/gamification/ranking                  # 팀 랭킹
GET  /api/gamification/my-points                # 내 포인트 내역
POST /api/gamification/award                    # 포인트 부여 (관리자)
GET  /api/gamification/quiz/today               # 오늘의 AI 퀴즈
POST /api/gamification/quiz/:id/answer          # 퀴즈 응답
GET  /api/gamification/risk-scores              # 위험도 점수
POST /api/gamification/risk-scores/calculate    # 재계산

# 알림
GET  /api/notifications           # 목록 (필터: 읽지 않은 것만)
POST /api/notifications/:id/read  # 읽음 처리
POST /api/notifications/read-all  # 전체 읽음 처리
```
</details>

---

## 권한 체계 (4단계 역할)

```
superadmin ─── 플랫폼 전체: 모든 회사, 통계, admin 계정 생성
    │
    admin ─── 회사 전체: 사업장, 사용자, 회사 내 모든 데이터
        │
        field_manager ─── 배정된 사업장: 사고 관리, 제보, TBM
            │
            worker ─── 모바일 PWA: 음성보고, 제보, 퀴즈, 안전수칙
```

하위 역할은 상위 역할의 권한을 상속합니다. 모든 엔드포인트는 역할과 리소스 소유권(company_id / site_id)을 동시에 검증합니다.

---

## 프로젝트 구조

```
ehs-compliance-chatbot/
├── packages/api/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py                  # 앱 팩토리 + 라우터 등록
│   │   ├── config.py                # Pydantic 설정
│   │   ├── database.py              # SQLAlchemy 엔진
│   │   ├── dependencies.py          # 인증 가드 (get_current_user, require_role)
│   │   ├── models/                  # 13개 모델 파일 → 22개 DB 테이블
│   │   ├── routers/                 # 19개 라우트 모듈 → 50+ 엔드포인트
│   │   └── services/
│   │       ├── rag_service.py       # FAISS 벡터 검색
│   │       ├── report_service.py    # PDF 생성 (ReportLab + 한글 폰트)
│   │       ├── law_api_client.py    # 국가법령정보센터 API 클라이언트
│   │       └── ai_agents/           # 4개 특화 AI 에이전트
│   ├── migrations/                  # Alembic (8개 마이그레이션)
│   ├── vector_db_law/               # FAISS 인덱스 (법률 784건)
│   ├── vector_db_rule/              # FAISS 인덱스 (규칙 13,802건)
│   └── scripts/                     # 유틸리티 + 시드 스크립트
│
├── apps/admin/                      # 관리자 웹앱
│   └── src/
│       ├── pages/                   # 18개 페이지 컴포넌트
│       ├── components/              # 레이아웃, 사이드바
│       ├── stores/authStore.ts      # Zustand JWT 상태 관리
│       └── lib/api.ts               # JWT 자동 갱신 API 클라이언트
│
├── apps/worker/                     # 작업자 모바일 PWA
│   └── src/
│       ├── pages/                   # 9개 모바일 페이지
│       ├── components/              # MobileLayout, BottomNav
│       └── stores/authStore.ts      # Zustand JWT 상태 관리
│
├── nginx/nginx.conf                 # 리버스 프록시 설정
├── docker-compose.yml               # 전체 서비스 오케스트레이션
└── .env.example                     # 환경 변수 템플릿
```

---

## 배포 (AWS)

플랫폼은 AWS에서 **https://safety-ai.team-ieum.com** 으로 운영됩니다.

```bash
# EC2 인스턴스에서
git clone <repo-url>
cd ehs-compliance-chatbot
cp .env.example .env
# .env에 운영 환경 값 설정

# 실행
docker-compose up -d --build

# 데모 데이터 투입
docker-compose exec api python scripts/seed_demo_data.py

# 로그 확인
docker-compose logs -f api
```

Nginx 라우팅:
- `/` → 관리자 대시보드
- `/worker/` → 작업자 PWA
- `/api/` → 백엔드 API
- SSL 종단: AWS ALB 또는 Certbot

---

## 이 프로젝트 살펴보기

포트폴리오로 리뷰하신다면, 아래 부분을 중점적으로 봐주세요:

1. **AI 통합** — ChatGPT 래퍼가 아닙니다. 4개의 특화 에이전트(`packages/api/app/services/ai_agents/`)가 각각 맞춤형 시스템 프롬프트, 구조화된 출력 파싱, 캐싱 전략을 갖추고 있습니다.

2. **RAG 파이프라인** — 14,500건 이상의 한국 산업안전 법령/규칙에 대한 실제 벡터 검색. `packages/api/app/services/rag_service.py`와 `vector_db_*/` 디렉토리를 확인하세요.

3. **듀얼 트랙 UX** — 관리자에게는 데이터 밀도 높은 대시보드를, 작업자에게는 음성 입력과 QR 스캔 중심의 모바일 PWA를 제공합니다. 사용 맥락에 맞는 서로 다른 인터페이스입니다.

4. **보안 설계** — 익명 제보는 사용자 신원을 일절 저장하지 않습니다 (user_id, IP, 디바이스 정보 없음). JWT 기반 역할별 접근 제어, 스트리밍 파일 사이즈 검증, CORS 설정.

5. **프로덕션 아키텍처** — Docker 멀티 서비스 오케스트레이션, PostgreSQL + Alembic 마이그레이션, Nginx 리버스 프록시, 헬스체크.

6. **실용적 AI 기능:**
   - 음성 → 구조화 데이터 파이프라인 (Whisper + GPT)
   - 가중 요인 모델 기반 자동 위험도 스코어링
   - 안전에 중요한 콘텐츠의 다국어 번역
   - 날씨 + 최근 사고 기반 AI 회의 안건 자동 생성

---

## 개발 참고

```bash
# 새 마이그레이션 생성
cd packages/api
alembic revision --autogenerate -m "설명"
alembic upgrade head

# 데이터베이스 초기화 (개발용)
rm ehs.db
alembic upgrade head
python scripts/seed_demo_data.py

# 핫 리로드 실행
uvicorn app.main:app --reload --port 8000
```

---

## 라이선스

MIT

---

<p align="center">
  <strong>SafetyAI</strong> — AI 기반 산업안전 리스크 관리 플랫폼<br/>
  <sub>FastAPI + React + OpenAI + FAISS | safety-ai.team-ieum.com</sub>
</p>
