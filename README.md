# SafetyAI — EHS 리스크 관리 플랫폼

> 기업별 산업안전 사고 데이터를 기반으로 반복 위험 유형을 분석하고, AI 예방 조치·법령 근거·월간 리포트를 자동 생성하는 기업형 EHS 관리 플랫폼

## 핵심 기능

### 관리자 트랙 (Admin Web)
| 기능 | 설명 |
|------|------|
| **사고/아차사고 관리** | 9개 유형, 4단계 심각도, 상태 워크플로우 (접수→조치중→완료→재발관리) |
| **AI 원인 분석** | GPT-4o 기반 근본 원인, 기여 요인, 예방 체크리스트 자동 생성 |
| **법령 근거 검색** | RAG(FAISS) + 국가법령정보센터 API 연동, 관련 법조문·사업주 의무·처벌 요약 |
| **대시보드** | 사고 통계 차트 (Recharts), KPI 카드, 산업안전 뉴스 AI 분석 |
| **월간 리포트** | PDF 자동 생성 (유형별/심각도별/상태별 집계 + AI 요약) |
| **익명 제보 관리** | AI 위험등급 분류, 조치 입력 → 제보자에게 피드백 |
| **위험 예측** | 가중 점수 모델 기반 공정별 위험도 스코어링 |

### 작업자 트랙 (Worker PWA)
| 기능 | 설명 |
|------|------|
| **음성 보고** | Whisper STT → GPT 구조화 파싱 → 사고 자동 등록 |
| **익명 제보** | 신원 비저장, AI 위험등급 분류, 토큰 기반 결과 확인 |
| **안전 퀴즈** | AI가 매일 새 문제 생성, 정답 시 포인트 적립 |
| **안전 랭킹** | 팀 단위 포인트 경쟁, 게이미피케이션 |
| **다국어 안전 안내** | QR 스캔 → 5개 언어 번역 (베트남/캄보디아/네팔/미얀마/영어) |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | FastAPI · SQLAlchemy 2.0 · Alembic · JWT (4-role) |
| **AI** | OpenAI GPT-4o-mini · Whisper · FAISS RAG · 4개 AI Agent |
| **Frontend** | React 19 · TypeScript · Vite 7 · TailwindCSS 4 · Recharts · Zustand |
| **Database** | SQLite (dev) / PostgreSQL (prod) · 18 tables |
| **Infra** | Docker · docker-compose · PWA |

---

## AI Agent 아키텍처

```
┌─────────────────────────────────────────┐
│           AI Agent Layer                 │
├──────────┬──────────┬──────────┬────────┤
│ NewsAgent│IncidentAg│ LawAgent │VoiceAg │
│          │          │          │        │
│ RSS 수집 │ 원인분석 │ 법령검색 │ STT    │
│ 유형분류 │ 체크리스트│ 의무요약 │ 파싱   │
│ 예방유의 │ 재발방지 │ 처벌안내 │ 구조화 │
└──────────┴──────────┴──────────┴────────┘
         ↑ BaseAgent (공유 OpenAI Client)
```

---

## 프로젝트 구조

```
packages/api/          FastAPI 백엔드 (40+ API endpoints)
  app/
    models/            18개 DB 테이블
    routers/           15개 라우터
    services/          RAG, Report, LawAPI, AI Agents
  migrations/          Alembic (7 migrations)
  vector_db_law/       법률 벡터DB (784 entries)
  vector_db_rule/      규칙 벡터DB (13,802 entries)

apps/admin/            관리자 웹앱 (React, port 3000)
  src/pages/           15개 페이지
  src/components/      레이아웃, 챗봇, 공통 컴포넌트

apps/worker/           작업자 PWA (React, port 3001)
  src/pages/           5개 모바일 페이지
```

---

## 실행 방법

### 1. 환경 변수 설정

```bash
cp packages/api/.env.example packages/api/.env
# .env 수정:
#   OPENAI_API_KEY=sk-...
#   LAW_API_KEY=공공데이터포털_인증키
#   JWT_SECRET_KEY=랜덤시크릿
```

### 2. 백엔드 실행

```bash
cd packages/api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Admin 프론트엔드

```bash
cd apps/admin
npm install
npm run dev  # http://localhost:3000
```

### 4. Worker 앱 (선택)

```bash
cd apps/worker
npm install
npm run dev  # http://localhost:3001
```

### 5. SuperAdmin 생성

```bash
cd packages/api
python scripts/create_superadmin.py
# → superadmin@safetyai.kr / super123
```

---

## API 엔드포인트 (40+)

<details>
<summary>전체 API 목록 보기</summary>

```
Auth:       POST /api/auth/register, login, refresh, me, users
Sites:      CRUD /api/sites, departments, processes, equipment, work-zones
Incidents:  CRUD /api/incidents, files
AI:         POST /api/ai/incidents/:id/analyze, checklist, legal
Analytics:  GET  /api/analytics/summary, by-type, by-month, by-status
Reports:    GET  /api/reports/monthly (PDF)
News:       GET  /api/news (RSS + AI분석)
Anonymous:  POST /api/anonymous-reports (인증불필요)
Voice:      POST /api/voice/transcribe, parse, submit
Law API:    GET  /api/law/search, detail/:id, articles
Guide:      CRUD /api/safety-guide, translate, qr, ack
Game:       GET  /api/gamification/ranking, quiz, risk-scores
SuperAdmin: GET  /api/superadmin/companies, stats
RAG:        POST /api/rag/ask (레거시 호환: POST /ask)
```

</details>

---

## 권한 체계 (4-Role)

| Role | 접근 범위 |
|------|-----------|
| `superadmin` | 플랫폼 전체 관리, 기업 목록, 통계 |
| `admin` | 기업 내 모든 사업장/사용자/데이터 |
| `field_manager` | 배정된 사업장만 (사고 등록/관리) |
| `worker` | Worker 앱 (음성보고/제보/퀴즈) |

---

## 데모 계정

| 역할 | 이메일 | 비밀번호 |
|------|--------|----------|
| SuperAdmin | `superadmin@safetyai.kr` | `super123` |
| Admin | `admin@safety.kr` | `admin123` |
| 현장담당자 | `field@safety.kr` | `field123` |
| 작업자 | `worker@safety.kr` | `worker123` |

---

## 라이선스

MIT

---

<p align="center">
  <b>SafetyAI</b> — AI 기반 산업안전 리스크 관리 플랫폼<br/>
  <sub>Built with FastAPI · React · OpenAI · FAISS</sub>
</p>
