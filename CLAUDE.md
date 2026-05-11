# EHS Risk Management Platform

## Project Overview
Enterprise EHS (Environment, Safety, Health) risk management SaaS platform.
Dual-track architecture: Admin (web) + Worker (mobile PWA), built on top of an existing RAG-based law compliance chatbot.

## Tech Stack
- **Backend:** FastAPI (Python 3.11) + SQLAlchemy 2.0 + Alembic + JWT auth
- **AI/RAG:** FAISS vector DB + OpenAI API (text-embedding-3-small, gpt-4o-mini, whisper-1)
- **Frontend:** React 19 + TypeScript + Vite 7 + TailwindCSS 4 + React Router 7 + Zustand + Recharts
- **PDF:** pdfplumber + pdf2image + pytesseract + camelot-py (extraction) / reportlab (generation)
- **Other:** qrcode (QR generation), bcrypt + python-jose (auth)
- **Deploy:** Docker + docker-compose

## Monorepo Structure
```
packages/api/                        # FastAPI backend
  app/
    main.py                          # App factory, agent init, all router registration
    config.py                        # pydantic-settings (EHS_DATABASE_URL, JWT, OpenAI, CORS_ORIGINS)
    database.py                      # SQLAlchemy sync engine/session
    dependencies.py                  # get_current_user, require_role

    models/
      company.py                     # Company
      site.py                        # Site
      user.py                        # User (superadmin/admin/field_manager/worker)
      master_data.py                 # Department, Process, Equipment, WorkZone
      incident.py                    # Incident (+ assignee/due_date), IncidentAttachment
      ai_analysis.py                 # AIAnalysisResult (cached, 24h TTL)
      anonymous_report.py            # AnonymousReport (no user identity stored)
      safety_guide.py                # SafetyGuide, Translation, TrainingRecord
      gamification.py                # SafetyPoint, SafetyQuiz, QuizResponse, RiskScore
      tbm.py                         # TBMSession, TBMAttendee
      risk_assessment.py             # RiskAssessment (AI-generated)
      notification.py                # Notification (in-app alerts)

    routers/
      auth.py                        # register, login, refresh, me, create user
      sites.py                       # Site CRUD (admin + superadmin)
      master_data.py                 # dept/process/equipment/work_zone CRUD
      incidents.py                   # Incident CRUD + filter/paging + assignee/due_date
      attachments.py                 # File upload/delete for incidents (streaming size check)
      ai_analysis.py                 # AI analyze/checklist/legal + DB caching
      analytics.py                   # Summary, by-type, by-month, by-status, insights
      reports.py                     # Monthly PDF report with AI summary
      news.py                        # Safety news RSS + AI analysis
      anonymous_reports.py           # Anonymous tip submit/check/admin
      voice.py                       # Whisper transcribe + GPT parse + submit
      safety_guide.py                # Guide CRUD, translate, QR, public view, ack
      gamification.py                # Points, ranking, quiz, risk scores
      tbm.py                         # TBM session CRUD + AI agenda generation
      risk_assessment.py             # AI risk assessment (hazards/matrix/measures/legal)
      notifications.py               # In-app notification list/read/read-all
      superadmin.py                  # Platform-wide admin (companies, stats)
      law_api.py                     # 국가법령정보센터 API proxy
      rag.py                         # Legacy RAG (law search engine)

    services/
      auth_service.py                # bcrypt + JWT
      rag_service.py                 # RAGService (FAISS + OpenAI)
      report_service.py              # PDF generation (reportlab + Korean font)
      law_api_client.py              # 국가법령정보센터 API client
      ai_agents/
        base.py                      # BaseAgent (_chat, _chat_json)
        news_agent.py                # RSS + GPT batch analysis (keyed cache)
        incident_agent.py            # Root cause + checklist + prevention
        law_agent.py                 # Legal basis search + regulation summary
        voice_agent.py               # Whisper STT + GPT structured parsing

  migrations/                        # Alembic (8 migrations)
  vector_db_law/                     # FAISS: 784 law entries
  vector_db_rule/                    # FAISS: 13,802 rule entries
  extracted_rule/                    # PDF extraction outputs
  scripts/                           # PDF processing utilities + create_superadmin.py

apps/admin/                          # Admin web app (React + Vite)
  src/
    router.tsx                       # 18 routes (landing + auth + 15 dashboard routes)
    stores/authStore.ts              # Zustand (JWT + user persist)
    lib/api.ts                       # JWT-aware fetch + auto-refresh
    pages/
      LandingPage.tsx                # Public landing page
      LoginPage.tsx                  # Login
      SignupPage.tsx                 # Company registration
      DashboardPage.tsx              # KPI cards + charts + AI insights + news feed + PDF
      IncidentListPage.tsx           # Filter/paging incident list
      IncidentFormPage.tsx           # New incident form
      IncidentDetailPage.tsx         # Detail + AI analysis/checklist/legal + assignee
      SafetyNewsPage.tsx             # RSS news + AI analysis expandable
      AnonymousReportsPage.tsx       # Admin: manage anonymous tips
      VoiceReportPage.tsx            # Record → Whisper → GPT → register
      TBMPage.tsx                    # TBM session management + AI agenda
      RiskAssessmentPage.tsx         # AI-powered risk assessment
      SafetyGuidePage.tsx            # Multilingual guide CRUD + QR
      QuizPage.tsx                   # AI daily quiz
      RankingPage.tsx                # Team safety ranking
      RiskScoresPage.tsx             # Risk prediction scores
      SitesPage.tsx                  # Site CRUD
      RagChatPage.tsx                # Legacy RAG chatbot
    components/
      layout/AppLayout.tsx, Sidebar.tsx

apps/worker/                         # Worker mobile PWA (React + Vite)
  src/
    router.tsx                       # 9 routes (login + 8 app routes)
    stores/authStore.ts              # Zustand (JWT + user persist)
    lib/api.ts                       # JWT-aware fetch + auto-refresh
    pages/
      LoginPage.tsx                  # Worker login
      HomePage.tsx                   # Quick action grid (6 cards)
      VoiceReportPage.tsx            # Voice recording → AI parse → submit
      AnonymousReportPage.tsx        # Anonymous tip + status check
      QuizPage.tsx                   # Daily safety quiz
      RankingPage.tsx                # Team ranking board
      SafetyGuidePage.tsx            # QR scan / guide ID → multilingual view + ack
      RiskScoresPage.tsx             # Process risk scores visualization
      MyPage.tsx                     # Profile + points + activity history
    components/
      MobileLayout.tsx               # Auth guard + dark theme wrapper
      BottomNav.tsx                  # 5-tab bottom navigation
```

## API Endpoints (50+)
```
# Auth
POST /api/auth/register              # Company signup
POST /api/auth/login                 # JWT tokens
POST /api/auth/refresh               # Token refresh
GET  /api/auth/me                    # Current user
POST /api/auth/users                 # Admin creates users

# Sites & Master Data
CRUD /api/sites                      # superadmin + admin can manage
CRUD /api/sites/:id/departments|processes|equipment|work-zones

# Incidents
GET/POST    /api/incidents           # List (filter/paging) / Create
GET/PATCH/DEL /api/incidents/:id     # Detail / Update (assignee/due_date) / Delete
POST/DEL    /api/incidents/:id/files # File upload/delete (streaming size check)

# AI Analysis (cached 24h in DB)
GET  /api/ai/incidents/:id/results   # Load all saved analyses
POST /api/ai/incidents/:id/analyze   # Root cause + risk level
POST /api/ai/incidents/:id/checklist # Prevention checklist
POST /api/ai/incidents/:id/legal     # Related laws + penalties
POST /api/ai/legal-basis             # Generic law search

# Analytics
GET  /api/analytics/summary          # Total + by_status + by_severity (field_mgr filtered)
GET  /api/analytics/by-type          # Incident type breakdown
GET  /api/analytics/by-month         # Monthly trend
GET  /api/analytics/by-status        # Status breakdown
GET  /api/analytics/insights         # AI insights (trends, overdue, patterns)

# Reports
GET  /api/reports/monthly            # PDF download (AI summary included)

# Safety News
GET  /api/news                       # RSS + GPT analysis (30min keyed cache)

# Anonymous Reports (submit/check = no auth)
POST /api/anonymous-reports          # Submit tip (AI risk classification)
GET  /api/anonymous-reports/check/:token  # Check status by token
GET  /api/anonymous-reports/admin    # Admin: list tips
PATCH /api/anonymous-reports/admin/:id    # Admin: respond/resolve

# Voice Report
POST /api/voice/transcribe           # Audio → text (Whisper)
POST /api/voice/parse                # Text → structured report (GPT)
POST /api/voice/submit               # Parsed data → incident

# TBM (Toolbox Meeting)
POST /api/tbm                        # Create TBM session (AI agenda)
GET  /api/tbm                        # List sessions for site
GET  /api/tbm/:id                    # Session detail
POST /api/tbm/:id/attend             # Record attendance

# Risk Assessment
POST /api/risk-assessment            # AI risk assessment (hazards/matrix/measures)
GET  /api/risk-assessment            # List assessments
GET  /api/risk-assessment/:id        # Detail
PATCH /api/risk-assessment/:id/status # Update status (with company auth check)

# Safety Guide (multilingual)
POST /api/safety-guide               # Create guide (Korean)
GET  /api/safety-guide/list          # List guides for site
POST /api/safety-guide/:id/translate # GPT translate (vi/en/km/ne/my)
GET  /api/safety-guide/qr/:id       # QR code PNG
GET  /api/safety-guide/:id          # Public view (no auth, for QR scan)
POST /api/safety-guide/:id/ack      # Training acknowledgment

# Gamification
GET  /api/gamification/ranking       # Team ranking
GET  /api/gamification/my-points     # My point history
POST /api/gamification/award         # Admin: award points
GET  /api/gamification/quiz/today    # AI-generated daily quiz
POST /api/gamification/quiz/:id/answer  # Answer quiz (+20 points)
GET  /api/gamification/risk-scores   # Risk scores by process
POST /api/gamification/risk-scores/calculate  # Recalculate

# Notifications
GET  /api/notifications              # List notifications (unread_only filter)
POST /api/notifications/:id/read     # Mark as read
POST /api/notifications/read-all     # Mark all as read

# Law API (국가법령정보센터)
GET  /api/law/search                 # Search laws
GET  /api/law/detail/:id             # Law detail
GET  /api/law/articles               # Law articles

# SuperAdmin
GET  /api/superadmin/companies       # All companies list
GET  /api/superadmin/stats           # Platform-wide statistics

# RAG (legacy law search)
POST /api/rag/ask | GET /api/rag/health | POST /api/rag/reload
GET  /health | POST /ask | POST /reload-db  (legacy compat)
```

## AI Agents Architecture
```
packages/api/app/services/ai_agents/
  base.py             # BaseAgent: shared OpenAI client, _chat(), _chat_json()
  news_agent.py       # RSS → batch GPT analysis (type/severity/tips/law), keyed cache
  incident_agent.py   # Incident → root cause / checklist / recurrence prevention
  law_agent.py        # Incident → related laws / employer obligations / penalties
  voice_agent.py      # Whisper STT → GPT structured parsing (type/severity/description)
```
All agents initialized at startup, share OpenAI client, have specialized system prompts.

## User Roles
- **superadmin:** Platform-wide management — all companies, stats, admin account creation
- **admin:** Full access within company — sites, users, incidents, reports, settings
- **field_manager:** Assigned site — register incidents, manage tips
- **worker:** Mobile — voice report, anonymous tips, quiz, safety guides, ranking

## DB Tables (22)
companies, sites, users, departments, processes, equipment, work_zones,
incidents, incident_attachments, ai_analysis_results, anonymous_reports,
safety_guides, safety_guide_translations, training_records,
safety_points, safety_quizzes, quiz_responses, risk_scores,
tbm_sessions, tbm_attendees, risk_assessments, notifications

## Development Commands
```bash
# Backend (from packages/api/)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Alembic
alembic revision --autogenerate -m "description"
alembic upgrade head

# Admin frontend (from apps/admin/)
npm install && npm run dev  # port 3000

# Worker frontend (from apps/worker/)
npm install && npm run dev  # port 3001

# Docker
docker-compose up
```

## Environment Variables (packages/api/.env)
- `OPENAI_API_KEY` — OpenAI API key (never commit)
- `EHS_DB_DIRS` — FAISS DB paths (default: vector_db_law,vector_db_rule)
- `OPENAI_TIMEOUT` — API timeout (default: 90)
- `EHS_DATABASE_URL` — DB URL (default: sqlite:///./ehs.db)
- `JWT_SECRET_KEY` — JWT signing secret (validated at startup, rejects insecure defaults)
- `CORS_ORIGINS` — Comma-separated allowed origins (default: *)
- `LAW_API_KEY` — 국가법령정보센터 API key
- `VITE_API_URL` — Backend URL for frontend (default: http://localhost:8000)

## Security Notes
- Static files mount serves only `uploads/` directory (not entire API package)
- CORS origins configurable via `CORS_ORIGINS` env var
- JWT secret validated at startup with warning for insecure defaults
- File uploads use streaming size check (64KB chunks, 10MB max)
- Anonymous reports store no user identity (no user_id, IP, device info)
- Incident model uses explicit `foreign_keys=` for relationship disambiguation

## Implementation Status
- **Phase 1 (done):** Monorepo + DB + Auth + Org structure
- **Phase 2 (done):** Incident CRUD + file attachments
- **Phase 3 (done):** AI analysis + checklist + legal basis (DB cached 24h)
- **Phase 4 (done):** Dashboard (Recharts) + analytics API + AI insights + monthly PDF report
- **Safety News (done):** Google News RSS + GPT analysis
- **AI Agents (done):** NewsAgent, IncidentAgent, LawAgent, VoiceAgent
- **Anonymous Reports (done):** Submit (no auth) + AI risk classification + admin manage
- **Voice Report (done):** Whisper STT → GPT parse → auto-register
- **Multilingual Guide (done):** Korean → 5 languages, QR code, training records
- **Gamification (done):** Points, ranking, AI quiz, risk prediction scoring
- **TBM (done):** Digital toolbox meeting + AI agenda generation
- **Risk Assessment (done):** AI-powered hazard/matrix/measures/legal analysis
- **Notifications (done):** In-app alerts for assignments, deadlines, tips
- **Assignee/Due Date (done):** Incident assignment workflow + overdue tracking
- **SuperAdmin (done):** Platform-wide management, 4-role auth
- **Worker PWA (done):** 9 pages — voice, anonymous, quiz, ranking, safety guide, risk scores
- **Security hardening (done):** Static mount fix, CORS config, JWT validation, streaming upload
- **Remaining:** Docker production config, deployment
