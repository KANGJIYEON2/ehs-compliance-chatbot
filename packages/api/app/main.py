"""EHS Risk Management API — App Factory"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings, API_PACKAGE_ROOT
import app.database as database
from app.database import init_db, Base
from app.models import *  # noqa: F401,F403 — register all models
from app.services.rag_service import rag_service
from app.services.ai_agents import NewsAgent, IncidentAgent, LawAgent

# AI Agent 싱글톤
news_agent = NewsAgent()
incident_agent = IncidentAgent()
law_agent = LawAgent()
from app.schemas.rag import AskRequest, AskResponse, ReloadRequest, HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # DB 초기화
    init_db(settings.EHS_DATABASE_URL)
    Base.metadata.create_all(bind=database.engine)
    # RAG 서비스 초기화 (OPENAI_API_KEY 없으면 스킵)
    try:
        rag_service.initialize(settings)
    except Exception as e:
        print(f"[WARNING] RAG service init failed: {e}")
    # AI Agents 초기화
    news_agent.initialize(settings)
    incident_agent.initialize(settings)
    law_agent.initialize(settings)
    yield


app = FastAPI(
    title="EHS Risk Management API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files: packages/api/ 루트를 /static 으로 서빙
app.mount("/static", StaticFiles(directory=str(API_PACKAGE_ROOT)), name="static")

# ── 라우터 등록 ──
from app.routers import rag, auth, sites, master_data, incidents, attachments, news, ai_analysis, analytics, reports, anonymous_reports  # noqa: E402

app.include_router(rag.router)
app.include_router(auth.router)
app.include_router(sites.router)
app.include_router(master_data.router)
app.include_router(incidents.router)
app.include_router(attachments.router)
app.include_router(news.router)
app.include_router(ai_analysis.router)
app.include_router(analytics.router)
app.include_router(reports.router)
app.include_router(anonymous_reports.router)


# ── 레거시 엔드포인트 (기존 FE ���환) ──

@app.get("/health", response_model=HealthResponse)
def legacy_health():
    return rag_service.health()


@app.post("/ask", response_model=AskResponse)
def legacy_ask(req: AskRequest, request: Request):
    static_base = str(request.base_url).rstrip("/")
    return rag_service.ask(
        question=req.question,
        topk=req.topk,
        mode=req.mode,
        ctx_chars=req.ctx_chars,
        dbs=req.dbs,
        static_base=static_base,
    )


@app.post("/reload-db")
def legacy_reload(req: ReloadRequest):
    return rag_service.reload(dbs=req.dbs)


# ── 로컬 실행 ──
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
