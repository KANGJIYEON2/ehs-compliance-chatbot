from fastapi import APIRouter, Request

from app.schemas.rag import AskRequest, AskResponse, ReloadRequest, HealthResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.get("/health", response_model=HealthResponse)
def health():
    return rag_service.health()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, request: Request):
    static_base = str(request.base_url).rstrip("/")
    return rag_service.ask(
        question=req.question,
        topk=req.topk,
        mode=req.mode,
        ctx_chars=req.ctx_chars,
        dbs=req.dbs,
        static_base=static_base,
    )


@router.post("/reload")
def reload_db(req: ReloadRequest):
    return rag_service.reload(dbs=req.dbs)
