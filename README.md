# SafetyAI — EHS 리스크 관리 플랫폼

> 관리자-작업자 듀얼 트랙 구조로, 사고 데이터 분석/예방 조치/법령 근거/음성 보고/다국어 안전 안내를 통합한 기업형 EHS 리스크 관리 SaaS 플랫폼

## 핵심 기능

### 관리자 트랙 (Admin Web — 18 pages)
| 기능 | 설명 |
|------|------|
| **사고/아차사고 관리** | 9개 유형, 4단계 심각도, 상태 워크플로우 (접수→조치중→완료→재발관리), 담당자 배정 + 기한 관리 |
| **AI 원인 분석** | GPT-4o 기반 근본 원인, 기여 요인, 예방 체크리스트 자동 생성 |
| **법령 근거 검색** | RAG(FAISS) + 국가법령정보센터 API 연동, 관련 법조문·사업주 의무·처벌 요약 |
| **대시보드** | KPI 카드, 사고 통계 차트 (Recharts), AI 인사이트, 기한 초과 경고 |
| **월간 리포트** | PDF 자동 생성 (유형별/심각도별/상태별 집계 + AI 요약) |
| **TBM 디지털화** | AI 기반 작업 전 안전회의 안건 자동 생성, 참석자 관리 |
| **위험성평가** | AI가 유해위험요인·위험도 매트릭스·감소대책·법령근거 자동 분석 |
| **익명 제보 관리** | AI 위험등급 분류, 조치 입력 → 제보자에게 피드백 |
| **안전 랭킹 / 퀴즈** | 팀별 포인트 랭킹, AI 일일 퀴즈 |
| **위험 예측** | 가중 점수 모델 기반 공정별 위험도 스코어링 |
| **다국어 안전 안내** | 한국어 작성 → GPT 5개국어 번역, QR코드 생성, 교육 이수 기록 |
| **알림 시스템** | 사고 배정·기한 초과·제보 접수 알림 |

### 작업자 트랙 (Worker PWA — 9 pages)
| 기능 | 설명 |
|------|------|
| **음성 보고** | Whisper STT → GPT 구조화 파싱 → 사고 자동 등록 |
| **익명 제보** | 신원 비저장, AI 위험등급 분류, 토큰 기반 결과 확인 |
| **안전 퀴즈** | AI가 매일 새 문제 생성, 정답 시 +20 포인트 |
| **안전 랭킹** | 팀 단위 포인트 경쟁, 메달 표시 |
| **안전수칙 조회** | QR 스캔/가이드 ID → 다국어 안전수칙 → 교육 이수 확인 |
| **위험 예측** | 내 사업장 공정별 위험도 스코어 + 요인 상세 |
| **마이페이지** | 포인트 현황, 활동 내역, 랭킹 확인 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| **Backend** | FastAPI · SQLAlchemy 2.0 · Alembic · JWT (4-role) |
| **AI** | OpenAI GPT-4o-mini · Whisper · FAISS RAG · 4개 AI Agent |
| **Frontend** | React 19 · TypeScript · Vite 7 · TailwindCSS 4 · Recharts · Zustand |
| **Database** | SQLite (dev) / PostgreSQL (prod) · 22 tables |
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
packages/api/          FastAPI 백엔드 (50+ API endpoints)
  app/
    models/            13개 모델 파일 (22 DB tables)
    routers/           19개 라우터
    services/          RAG, Report, LawAPI, AI Agents
  migrations/          Alembic (8 migrations)
  vector_db_law/       법률 벡터DB (784 entries)
  vector_db_rule/      규칙 벡터DB (13,802 entries)

apps/admin/            관리자 웹앱 (React, port 3000)
  src/pages/           18개 페이지
  src/components/      레이아웃, 사이드바, 공통 컴포넌트

apps/worker/           작업자 PWA (React, port 3001)
  src/pages/           9개 모바일 페이지
  src/components/      MobileLayout, BottomNav
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
#   CORS_ORIGINS=http://localhost:3000,http://localhost:3001
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

### 4. Worker 앱

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

## API 엔드포인트 (50+)

<details>
<summary>전체 API 목록 보기</summary>

```
Auth:           POST /api/auth/register, login, refresh, me, users
Sites:          CRUD /api/sites, departments, processes, equipment, work-zones
Incidents:      CRUD /api/incidents, files (담당자 배정 + 기한)
AI:             POST /api/ai/incidents/:id/analyze, checklist, legal
Analytics:      GET  /api/analytics/summary, by-type, by-month, by-status, insights
Reports:        GET  /api/reports/monthly (PDF)
News:           GET  /api/news (RSS + AI분석, 30분 캐싱)
Anonymous:      POST /api/anonymous-reports (인증불필요)
Voice:          POST /api/voice/transcribe, parse, submit
Law API:        GET  /api/law/search, detail/:id, articles
Guide:          CRUD /api/safety-guide, translate, qr, ack
Game:           GET  /api/gamification/ranking, quiz, risk-scores
TBM:            CRUD /api/tbm (AI 안건 생성, 참석자)
Risk Assess:    CRUD /api/risk-assessment (AI 위험성평가)
Notifications:  GET  /api/notifications, read, read-all
SuperAdmin:     GET  /api/superadmin/companies, stats
RAG:            POST /api/rag/ask (레거시 호환: POST /ask)
```

</details>

---

## 권한 체계 (4-Role)

| Role | 접근 범위 |
|------|-----------|
| `superadmin` | 플랫폼 전체 관리, 기업 목록, 통계, admin 계정 생성 |
| `admin` | 기업 내 모든 사업장/사용자/데이터 |
| `field_manager` | 배정된 사업장만 (사고 등록/관리) |
| `worker` | Worker 앱 (음성보고/제보/퀴즈/랭킹/안전수칙) |

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
