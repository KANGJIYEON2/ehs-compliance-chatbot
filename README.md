<p align="center">
  <img src="https://img.shields.io/badge/SafetyAI-EHS%20Platform-0066FF?style=for-the-badge&logo=shield&logoColor=white" alt="SafetyAI" />
</p>

<h1 align="center">SafetyAI — Enterprise EHS Risk Management Platform</h1>

<p align="center">
  AI-powered Environment, Health & Safety management SaaS with dual-track architecture<br/>
  <strong>Admin Web Dashboard</strong> (18 pages) + <strong>Worker Mobile PWA</strong> (9 pages)
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
  <a href="https://safety-ai.team-ieum.com">Live Demo</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#api-reference">API Reference</a> &middot;
  <a href="#architecture">Architecture</a>
</p>

---

## Why I Built This

Korean workplaces face a serious industrial safety challenge. In 2022 alone, over 2,000 workers died in occupational accidents. The **Serious Accidents Punishment Act** (중대재해처벌법) now holds executives criminally liable for safety failures — yet most small-to-medium manufacturers still manage safety with paper checklists and Excel spreadsheets.

I wanted to build a platform that:

1. **Eliminates paper-based safety management** — digitize incident reporting, TBM meetings, risk assessments
2. **Makes AI practical for safety teams** — not a chatbot gimmick, but embedded AI that analyzes root causes, predicts risks, and generates actionable compliance checklists
3. **Bridges the language gap** — foreign workers (Vietnamese, Cambodian, Nepali, Myanmar, English) get safety instructions in their native language via QR codes
4. **Empowers workers, not just managers** — anonymous reporting, voice-based incident submission, gamified safety behavior

This started as a RAG-based law compliance chatbot, then evolved into a full-stack EHS platform after realizing that legal search alone doesn't save lives — **proactive risk management** does.

---

## Live Demo

> **https://safety-ai.team-ieum.com**

| Role | Email | Password | Access |
|------|-------|----------|--------|
| Super Admin | `superadmin@safetyai.kr` | `super123` | Platform-wide management |
| Admin | `admin@hankook-steel.kr` | `admin123` | Full company access (Admin dashboard) |
| Field Manager | `park.jm@hankook-steel.kr` | `field123` | Assigned site only |
| Worker | `kim.worker@hankook-steel.kr` | `worker123` | Worker PWA (`/worker/`) |

**Admin Dashboard:** https://safety-ai.team-ieum.com
**Worker PWA:** https://safety-ai.team-ieum.com/worker/

---

## Key Features

### Admin Track (Web Dashboard)

| Feature | What it does |
|---------|-------------|
| **Incident Management** | 9 incident types, 4 severity levels, status workflow (reported → investigating → resolved → monitoring), assignee + due date tracking |
| **AI Root Cause Analysis** | GPT-4o analyzes incidents → root causes, contributing factors, prevention checklists, legal basis |
| **Legal Compliance (RAG)** | FAISS vector search (14,500+ law/rule entries) + National Law API → relevant statutes, employer obligations, penalties |
| **Dashboard & Analytics** | KPI cards, trend charts (Recharts), AI-generated insights, overdue warnings |
| **Monthly PDF Reports** | Auto-generated reports with stats breakdown + AI executive summary |
| **TBM Digitization** | AI generates pre-shift safety meeting agendas, tracks attendance |
| **Risk Assessment** | AI identifies hazards → risk matrix → mitigation measures → legal requirements |
| **Anonymous Reports** | Workers submit tips without identity → AI risk classification → admin response loop |
| **Multilingual Safety Guides** | Write in Korean → GPT translates to 5 languages → QR code → training acknowledgment |
| **Gamification** | Points, team rankings, AI daily quizzes, risk prediction scores |
| **Notifications** | Real-time alerts for assignments, overdue items, new reports |

### Worker Track (Mobile PWA)

| Feature | What it does |
|---------|-------------|
| **Voice Report** | Speak into phone → Whisper STT → GPT structures the data → auto-creates incident |
| **Anonymous Tips** | Zero-identity reporting, token-based status checking |
| **Safety Quiz** | AI generates daily questions, +20 points per correct answer |
| **Team Ranking** | Gamified safety competition with medals |
| **Safety Guide Viewer** | QR scan → multilingual safety instructions → acknowledge completion |
| **Risk Scores** | Visual risk levels for each process in your site |
| **My Page** | Points history, activity log, personal ranking |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy                       │
│   /           → Admin React App                              │
│   /worker/    → Worker React PWA                             │
│   /api/       → FastAPI Backend                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐   ┌────────────────────────────┐  │
│  │   Admin Dashboard     │   │    Worker PWA (Mobile)     │  │
│  │   React 19 + Vite 7   │   │    React 19 + Vite 7      │  │
│  │   18 pages            │   │    9 pages                 │  │
│  │   TailwindCSS 4       │   │    Bottom nav + dark theme │  │
│  └──────────┬───────────┘   └──────────────┬─────────────┘  │
│             │                               │                │
│             └───────────────┬───────────────┘                │
│                             ▼                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI Backend (Python 3.11)             │   │
│  │   50+ REST endpoints · JWT 4-role auth · SQLAlchemy   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                   AI Agent Layer                       │   │
│  │  ┌──────────┬────────────┬──────────┬─────────────┐  │   │
│  │  │NewsAgent │IncidentAg  │ LawAgent │ VoiceAgent  │  │   │
│  │  │RSS+GPT   │Root cause  │ RAG+Law  │ Whisper+GPT │  │   │
│  │  └──────────┴────────────┴──────────┴─────────────┘  │   │
│  │         BaseAgent (shared OpenAI client)               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  FAISS Vector DBs        PostgreSQL 16                │   │
│  │  784 laws + 13,802 rules  22 tables                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, JWT (python-jose + bcrypt) |
| **AI/ML** | OpenAI GPT-4o-mini, Whisper-1, text-embedding-3-small, FAISS |
| **Frontend** | React 19, TypeScript, Vite 7, TailwindCSS 4, Zustand, Recharts, Framer Motion |
| **Database** | PostgreSQL 16 (prod) / SQLite (dev), 22 tables |
| **PDF** | pdfplumber + pytesseract (extraction), ReportLab (generation) |
| **Infrastructure** | Docker, docker-compose, Nginx, AWS EC2 |

### Database Schema (22 tables)

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

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone
git clone https://github.com/your-username/ehs-compliance-chatbot.git
cd ehs-compliance-chatbot

# Configure environment
cp .env.example .env
# Edit .env: set JWT_SECRET_KEY, OPENAI_API_KEY

# Start all services
docker-compose up --build

# Seed test data (in another terminal)
docker-compose exec api python scripts/seed_demo_data.py

# Access
# Admin:  http://localhost
# Worker: http://localhost/worker/
# API:    http://localhost/api/docs
```

### Option 2: Local Development

```bash
# 1. Backend
cd packages/api
pip install -r requirements.txt
cp .env.example .env  # Edit with your keys
alembic upgrade head
python scripts/seed_demo_data.py  # Populate test data
uvicorn app.main:app --reload --port 8000

# 2. Admin Frontend (new terminal)
cd apps/admin
npm install
npm run dev  # → http://localhost:3000

# 3. Worker Frontend (new terminal)
cd apps/worker
npm install
npm run dev  # → http://localhost:3001
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | Yes | Random secret for JWT signing (min 32 chars) |
| `OPENAI_API_KEY` | Yes | OpenAI API key (for AI features) |
| `EHS_DATABASE_URL` | No | DB URL (default: `sqlite:///./ehs.db`) |
| `LAW_API_KEY` | No | Korean National Law API key |
| `CORS_ORIGINS` | No | Allowed origins (default: `*`) |
| `DB_PASSWORD` | No | PostgreSQL password (Docker only) |

---

## API Reference

The platform exposes **50+ REST endpoints** organized into 19 route groups.

<details>
<summary><strong>Authentication & Users</strong></summary>

```
POST /api/auth/register        # Company signup (creates company + admin)
POST /api/auth/login           # Returns access + refresh JWT tokens
POST /api/auth/refresh         # Refresh access token
GET  /api/auth/me              # Current user profile
POST /api/auth/users           # Admin creates users (field_manager/worker)
```
</details>

<details>
<summary><strong>Sites & Master Data</strong></summary>

```
CRUD /api/sites                          # Site management
CRUD /api/sites/:id/departments          # Departments within site
CRUD /api/sites/:id/processes            # Production processes
CRUD /api/sites/:id/equipment            # Equipment registry
CRUD /api/sites/:id/work-zones           # Physical work zones
```
</details>

<details>
<summary><strong>Incidents</strong></summary>

```
GET  /api/incidents            # List with filter/paging (type, severity, status, date)
POST /api/incidents            # Create incident
GET  /api/incidents/:id        # Detail view
PATCH /api/incidents/:id       # Update (status, assignee, due_date)
DELETE /api/incidents/:id       # Delete
POST /api/incidents/:id/files  # Upload attachment (streaming, 10MB max)
DELETE /api/incidents/:id/files/:fid  # Remove attachment
```
</details>

<details>
<summary><strong>AI Analysis (cached 24h)</strong></summary>

```
GET  /api/ai/incidents/:id/results    # Load all saved analyses
POST /api/ai/incidents/:id/analyze    # Root cause + risk level + contributing factors
POST /api/ai/incidents/:id/checklist  # Prevention checklist generation
POST /api/ai/incidents/:id/legal      # Related laws + penalties + employer obligations
POST /api/ai/legal-basis              # Generic law search (not incident-specific)
```
</details>

<details>
<summary><strong>Analytics & Reports</strong></summary>

```
GET /api/analytics/summary     # Total count + by_status + by_severity
GET /api/analytics/by-type     # Incident type breakdown
GET /api/analytics/by-month    # Monthly trend (12 months)
GET /api/analytics/by-status   # Status distribution
GET /api/analytics/insights    # AI-generated insights (trends, patterns, risks)
GET /api/reports/monthly       # PDF report download
```
</details>

<details>
<summary><strong>Voice Report</strong></summary>

```
POST /api/voice/transcribe     # Audio file → text (Whisper STT)
POST /api/voice/parse          # Text → structured incident data (GPT)
POST /api/voice/submit         # Parsed data → create incident record
```
</details>

<details>
<summary><strong>Anonymous Reports</strong></summary>

```
POST  /api/anonymous-reports              # Submit (no auth required)
GET   /api/anonymous-reports/check/:token # Check status by anonymous token
GET   /api/anonymous-reports/admin        # Admin: list all reports
PATCH /api/anonymous-reports/admin/:id    # Admin: respond/resolve
```
</details>

<details>
<summary><strong>TBM, Risk Assessment, Guides, Gamification, Notifications</strong></summary>

```
# TBM (Toolbox Meeting)
POST /api/tbm                  # Create session (AI generates agenda)
GET  /api/tbm                  # List sessions
GET  /api/tbm/:id              # Detail with attendees
POST /api/tbm/:id/attend       # Record attendance

# Risk Assessment
POST  /api/risk-assessment              # AI analysis (hazards/matrix/measures/legal)
GET   /api/risk-assessment              # List assessments
GET   /api/risk-assessment/:id          # Detail
PATCH /api/risk-assessment/:id/status   # Update status

# Safety Guides
POST /api/safety-guide                 # Create guide (Korean)
GET  /api/safety-guide/list            # List guides
POST /api/safety-guide/:id/translate   # GPT translate (vi/en/km/ne/my)
GET  /api/safety-guide/qr/:id         # QR code PNG
GET  /api/safety-guide/:id            # Public view (no auth, for QR scan)
POST /api/safety-guide/:id/ack        # Acknowledge training

# Gamification
GET  /api/gamification/ranking                  # Team ranking
GET  /api/gamification/my-points                # Point history
POST /api/gamification/award                    # Award points (admin)
GET  /api/gamification/quiz/today               # Daily AI quiz
POST /api/gamification/quiz/:id/answer          # Submit answer
GET  /api/gamification/risk-scores              # Risk scores
POST /api/gamification/risk-scores/calculate    # Recalculate

# Notifications
GET  /api/notifications           # List (filter: unread_only)
POST /api/notifications/:id/read  # Mark read
POST /api/notifications/read-all  # Mark all read
```
</details>

---

## Authorization (4-Role System)

```
superadmin ─── Platform-wide: all companies, stats, admin creation
    │
    admin ─── Company-wide: sites, users, all data within company
        │
        field_manager ─── Assigned site only: incidents, reports, TBM
            │
            worker ─── Mobile PWA: voice report, tips, quiz, guides
```

Each role inherits permissions downward. Endpoints validate both role and resource ownership (company_id / site_id).

---

## Project Structure

```
ehs-compliance-chatbot/
├── packages/api/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # App factory + router registration
│   │   ├── config.py                # Pydantic settings
│   │   ├── database.py              # SQLAlchemy engine
│   │   ├── dependencies.py          # Auth guards (get_current_user, require_role)
│   │   ├── models/                  # 13 model files → 22 DB tables
│   │   ├── routers/                 # 19 route modules → 50+ endpoints
│   │   └── services/
│   │       ├── rag_service.py       # FAISS vector search
│   │       ├── report_service.py    # PDF generation (ReportLab + Korean fonts)
│   │       ├── law_api_client.py    # National Law Information Center API
│   │       └── ai_agents/           # 4 specialized AI agents
│   ├── migrations/                  # Alembic (8 versions)
│   ├── vector_db_law/               # FAISS index (784 law entries)
│   ├── vector_db_rule/              # FAISS index (13,802 rule entries)
│   └── scripts/                     # Utilities + seed scripts
│
├── apps/admin/                      # Admin Web App
│   └── src/
│       ├── pages/                   # 18 page components
│       ├── components/              # Layout, Sidebar
│       ├── stores/authStore.ts      # Zustand JWT state
│       └── lib/api.ts               # API client with auto-refresh
│
├── apps/worker/                     # Worker Mobile PWA
│   └── src/
│       ├── pages/                   # 9 mobile pages
│       ├── components/              # MobileLayout, BottomNav
│       └── stores/authStore.ts      # Zustand JWT state
│
├── nginx/nginx.conf                 # Reverse proxy config
├── docker-compose.yml               # Full stack orchestration
└── .env.example                     # Environment template
```

---

## Deployment (AWS)

The platform is deployed at **https://safety-ai.team-ieum.com** on AWS.

```bash
# On EC2 instance
git clone <repo-url>
cd ehs-compliance-chatbot
cp .env.example .env
# Edit .env with production values

# Start
docker-compose up -d --build

# Seed demo data
docker-compose exec api python scripts/seed_demo_data.py

# Logs
docker-compose logs -f api
```

Nginx handles routing:
- `/` → Admin dashboard
- `/worker/` → Worker PWA
- `/api/` → Backend API
- SSL termination via AWS ALB or Certbot

---

## How to Explore This Project

If you're reviewing this as a portfolio piece, here's what to look at:

1. **AI Integration** — Not a wrapper around ChatGPT. Four specialized agents (`packages/api/app/services/ai_agents/`) each with tailored system prompts, structured output parsing, and caching strategies.

2. **RAG Pipeline** — Real vector search over 14,500+ Korean safety law/regulation entries. See `packages/api/app/services/rag_service.py` and the `vector_db_*/` directories.

3. **Dual-Track UX** — Admin gets data-dense dashboards; workers get a mobile-first PWA with voice input, QR scanning, and minimal text entry. Different interfaces for different contexts.

4. **Security Design** — Anonymous reports store zero user identity (no user_id, no IP, no device fingerprint). JWT with role-based access control, streaming file size validation, CORS configuration.

5. **Production Architecture** — Docker multi-service orchestration, PostgreSQL with Alembic migrations, Nginx reverse proxy, health checks.

6. **Practical AI Features:**
   - Voice → structured data pipeline (Whisper + GPT)
   - Automated risk scoring with weighted factor model
   - Multilingual translation for safety-critical content
   - AI-generated meeting agendas based on weather + recent incidents

---

## Development Notes

```bash
# Create new migration
cd packages/api
alembic revision --autogenerate -m "description"
alembic upgrade head

# Reset database (dev only)
rm ehs.db
alembic upgrade head
python scripts/seed_demo_data.py

# Run with hot reload
uvicorn app.main:app --reload --port 8000
```

---

## License

MIT

---

<p align="center">
  <strong>SafetyAI</strong> — AI-Powered Industrial Safety Risk Management<br/>
  <sub>Built with FastAPI + React + OpenAI + FAISS | Deployed at safety-ai.team-ieum.com</sub>
</p>
