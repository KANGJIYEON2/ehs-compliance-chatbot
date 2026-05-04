# EHS Risk Management Platform

## Project Overview
Enterprise EHS (Environment, Safety, Health) risk management SaaS platform.
Dual-track architecture: Admin (web) + Worker (mobile PWA), built on top of an existing RAG-based law compliance chatbot.

## Tech Stack
- **Backend:** FastAPI (Python 3.11) + SQLAlchemy 2.0 + Alembic + JWT auth
- **AI/RAG:** FAISS vector DB + OpenAI API (text-embedding-3-small, gpt-4o-mini)
- **Frontend:** React 19 + TypeScript + Vite 7 + TailwindCSS 4 + React Router 7 + Zustand
- **PDF Pipeline:** pdfplumber + pdf2image + pytesseract + camelot-py
- **Deploy:** Docker + docker-compose

## Monorepo Structure
```
packages/api/                    # FastAPI backend
  app/
    main.py                      # App factory + legacy /ask compat
    config.py                    # pydantic-settings (EHS_DATABASE_URL, JWT, OpenAI)
    database.py                  # SQLAlchemy sync engine/session
    dependencies.py              # get_current_user, require_role
    models/                      # Company, Site, User, Department, Process, Equipment, WorkZone
    schemas/                     # Pydantic request/response models
    routers/
      auth.py                    # register, login, refresh, me, create user
      rag.py                     # /api/rag/ask, /api/rag/health, /api/rag/reload
      sites.py                   # Site CRUD (company-scoped)
      master_data.py             # dept/process/equipment/work_zone CRUD (site-scoped)
    services/
      auth_service.py            # bcrypt + python-jose JWT
      rag_service.py             # RAGService class (extracted from old be/main.py)
  migrations/                    # Alembic
  vector_db_law/                 # FAISS index + metadata
  vector_db_rule/                # FAISS index + metadata
  extracted_rule/                # PDF extraction outputs
  scripts/                       # PDF processing utilities

apps/admin/                      # Admin web app (React + Vite)
  src/
    router.tsx                   # React Router config
    stores/authStore.ts          # Zustand (JWT + user persist)
    lib/api.ts                   # JWT-aware fetch wrapper with auto-refresh
    pages/                       # Login, Signup, Dashboard, RagChat, Sites
    components/
      layout/                    # AppLayout, Sidebar
      chat/                      # Existing RAG chatbot components

apps/worker/                     # Worker mobile PWA (Phase 5 placeholder)

be/                              # Legacy backend (kept for reference)
fe/                              # Legacy frontend (kept for reference)
```

## API Endpoints
```
# Auth
POST /api/auth/register          # Company signup (creates company + admin user)
POST /api/auth/login             # JWT tokens
POST /api/auth/refresh           # Token refresh
GET  /api/auth/me                # Current user
POST /api/auth/users             # Admin creates field_manager/worker

# Sites & Master Data
GET/POST        /api/sites
GET/PATCH/DEL   /api/sites/:id
CRUD            /api/sites/:id/departments
CRUD            /api/sites/:id/processes
CRUD            /api/sites/:id/equipment
CRUD            /api/sites/:id/work-zones

# RAG (law search engine)
POST /api/rag/ask                # RAG query
GET  /api/rag/health             # DB status
POST /api/rag/reload             # Reload vector DBs

# Legacy (backward compat for old frontend)
GET  /health
POST /ask
POST /reload-db
```

## User Roles
- **admin:** Full access, can create sites/users, manage everything
- **field_manager:** Assigned to specific site, can register incidents
- **worker:** Mobile app access, voice reports, anonymous tips

## Development Commands
```bash
# Backend (from packages/api/)
pip install -r requirements.txt
uvicorn app.main:app --reload

# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Admin frontend (from apps/admin/)
npm install && npm run dev    # runs on port 3000, proxies /api to localhost:8000

# Docker
docker-compose up
```

## Environment Variables (packages/api/.env)
- `OPENAI_API_KEY` — OpenAI API key (never commit)
- `EHS_DB_DIRS` — Comma-separated DB paths (default: vector_db_law,vector_db_rule)
- `OPENAI_TIMEOUT` — API timeout seconds (default 90)
- `EHS_DATABASE_URL` — SQLAlchemy DB URL (default: sqlite:///./ehs.db)
- `JWT_SECRET_KEY` — JWT signing secret
- `VITE_API_URL` — Backend URL for frontend (default: http://localhost:8000)

## Development Direction
See `docs/PRODUCT_PLAN.md` for full product plan.
- **Phase 1 (done):** Monorepo + DB + Auth + Org structure
- **Phase 2:** Incident management CRUD
- **Phase 3:** AI analysis + prevention checklists
- **Phase 4:** Dashboard + reports
- **Phase 5:** Worker track (voice, anonymous tips, multilingual, gamification)
- **Phase 6:** Risk prediction scoring
