# be/main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FastAPI: 법령/규칙 통합 RAG API (이미지 URL 절대경로 반환)

엔드포인트
- GET  /health
- GET  /static/...           : 정적 파일(예: extracted_rule/images/*.png)
- POST /ask                  : {"question": "...", "topk": 5, "mode": "auto|law|rule", "ctx_chars": 6000, "dbs": ["vector_db_law","vector_db_rule"]}
- POST /reload-db            : {"dbs": ["vector_db_law","vector_db_rule"]}  # 없으면 환경변수/기본값 사용

환경변수(.env)
- OPENAI_API_KEY=sk-xxxx
- EHS_DB_DIRS=vector_db_law,vector_db_rule    # 선택: 서버 기동 시 기본 로드 DB들
- OPENAI_TIMEOUT=60                            # 선택: 초 단위
"""

from __future__ import annotations
import os, json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import faiss
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI

# ===== 설정 =====
EMBED_MODEL = "text-embedding-3-small"   # 1536차원
CHAT_MODEL  = "gpt-4o-mini"
DEFAULT_CTX_CHARS = 6000

# 프로젝트 루트(= be 디렉터리)
PROJECT_ROOT = Path(__file__).resolve().parent

app = FastAPI(title="EHS Law/Rule RAG API", version="1.1.4")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ✅ 정적 파일 서빙: 프로젝트 루트를 /static 으로 공개
# 예) be/extracted_rule/images/foo.png -> http://127.0.0.1:8000/static/extracted_rule/images/foo.png
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT)), name="static")

# ===== 전역 상태 =====
_client: Optional[OpenAI] = None
# 각 원소: (faiss.Index, meta(list[dict]), label(str))
_dbs: List[Tuple[faiss.Index, List[Dict[str,Any]], str]] = []


# ===== 유틸 =====
def _env_db_dirs() -> List[str]:
    # EHS_DB_DIRS=vector_db_law,vector_db_rule
    raw = os.getenv("EHS_DB_DIRS", "").strip()
    if not raw:
        # 기존 호환: 단일 폴더 vector_db
        return ["vector_db"]
    return [p.strip() for p in raw.split(",") if p.strip()]

def load_client() -> OpenAI:
    load_dotenv()
    api = os.getenv("OPENAI_API_KEY")
    if not api:
        raise RuntimeError("❌ .env에 OPENAI_API_KEY가 없습니다.")
    timeout = float(os.getenv("OPENAI_TIMEOUT", "60"))
    return OpenAI(api_key=api, timeout=timeout)

def load_db_one(db_dir: Path) -> Tuple[faiss.Index, List[Dict[str,Any]], str]:
    idx = db_dir / "laws.index"
    meta = db_dir / "laws_meta.json"
    if not idx.exists() or not meta.exists():
        raise FileNotFoundError(f"❌ 벡터DB 파일을 찾을 수 없습니다: {idx}, {meta}")
    return faiss.read_index(str(idx)), json.loads(meta.read_text(encoding="utf-8")), db_dir.name

def load_dbs(paths: List[str]) -> List[Tuple[faiss.Index, List[Dict[str,Any]], str]]:
    out = []
    for p in paths:
        index, meta, label = load_db_one(Path(p).resolve())
        out.append((index, meta, label))
    if not out:
        raise RuntimeError("❌ 로드할 DB가 없습니다.")
    return out

def embed(texts: List[str]) -> np.ndarray:
    if _client is None:
        raise RuntimeError("OpenAI client not initialized")
    resp = _client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    return np.array(vecs, dtype="float32")

def _guess_level(law_name: Optional[str], article_id: Optional[str], src_type: Optional[str]) -> str:
    ln = (law_name or "")
    aid = (article_id or "")
    t = (src_type or "").lower()
    if "별표" in aid or "annex" in t or "table" in t or "ocr" in t:
        return "별표"
    if "규칙" in ln or "기준" in ln:
        return "시행규칙"
    if "시행령" in ln:
        return "시행령"
    if "법" in ln:
        return "법률"
    return "기타"

def _ref_label_no_db(h: Dict[str, Any]) -> str:
    """라벨(답변/표시용): DB명은 제외"""
    ln  = h.get("law_name") or "법령/규칙"
    aid = h.get("article_id") or "-"
    typ = h.get("type")
    lvl = h.get("level")
    parts = [ln, aid]
    if typ: parts.append(typ)
    if lvl: parts.append(lvl)
    return " · ".join([p for p in parts if p and p != "-"])

def _meta_image_to_url(m: Dict[str, Any], static_base: str) -> Optional[str]:
    """
    메타에 image_url이 있으면:
      - 절대 URL이면 그대로
      - 상대 URL이면 static_base 붙여 절대화
    image_path / image_rel이 있으면:
      - PROJECT_ROOT 기준 상대경로 계산 후 static_base + '/static/...' 로 절대화
    """
    url = m.get("image_url")
    if isinstance(url, str) and url.strip():
        if url.startswith("http://") or url.startswith("https://"):
            return url
        # 상대경로일 경우 서버 베이스 붙이기
        return f"{static_base.rstrip('/')}/{url.lstrip('/')}"

    p = m.get("image_path") or m.get("image_rel")
    if not p:
        return None

    raw = Path(p)
    abs_path = raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()

    try:
        rel = abs_path.resolve().relative_to(PROJECT_ROOT.resolve())
        return f"{static_base.rstrip('/')}/static/{rel.as_posix()}"
    except Exception:
        # 상대 경로 문자열일 가능성에 대한 best-effort
        p_norm = str(raw).replace("\\", "/").lstrip("./")
        return f"{static_base.rstrip('/')}/static/{p_norm}"

def search_many(
    dbs: List[Tuple[faiss.Index, List[Dict[str,Any]], str]],
    qvec: np.ndarray,
    topk: int,
    static_base: str,  # ✅ 절대 URL 생성용
) -> List[Dict[str, Any]]:
    if not dbs:
        raise RuntimeError("Vector DB not loaded")
    all_hits: List[Dict[str, Any]] = []
    per_k = max(topk, 5)
    for index, meta, label in dbs:
        k = min(per_k, len(meta))
        D, I = index.search(qvec, k)
        seen = set()
        for idx, dist in zip(I[0], D[0]):
            if 0 <= idx < len(meta):
                m = meta[idx]
                key = (m.get("law_name"), m.get("article_id"), hash((m.get("content") or "")[:256]))
                if key in seen:
                    continue
                seen.add(key)

                hit: Dict[str, Any] = {
                    "law_name": m.get("law_name"),
                    "article_id": m.get("article_id"),
                    "content": m.get("content", ""),
                    "type": m.get("type") or m.get("source_type"),
                    "db": label,
                    "distance": float(dist),
                    # 표 렌더링 힌트
                    "content_format": m.get("content_format"),
                }
                hit["level"] = _guess_level(hit["law_name"], hit["article_id"], hit["type"])
                hit["label"] = _ref_label_no_db(hit)

                img_url = _meta_image_to_url(m, static_base)
                if img_url:
                    hit["image_url"] = img_url

                all_hits.append(hit)

    all_hits.sort(key=lambda x: x["distance"])
    return all_hits[:topk]

def _prioritize_hits(hits: List[Dict[str, Any]], question: str) -> List[Dict[str, Any]]:
    q = question or ""
    q_bias = 0.0
    if any(k in q for k in ["밀폐공간", "별표", "표", "그림"]):
        q_bias = 0.05  # 질문이 별표 맥락이면 살짝 더 밀어줌

    def score(h: Dict[str, Any]) -> float:
        s = h["distance"]
        if h.get("level") == "별표":
            s -= 0.15
        elif h.get("level") == "시행규칙":
            s -= 0.06
        if "별표" in (h.get("article_id") or ""):
            s -= 0.05
        return s - q_bias

    return sorted(hits, key=score)

def build_context(hits: List[Dict[str, Any]], max_chars: int) -> str:
    parts: List[str] = []
    total = 0
    for h in hits:
        head = f"[{h['label']}]"
        body = (h.get("content") or "").strip()
        block = f"{head}\n{body}"
        if total + len(block) + 4 > max_chars:
            break
        parts.append(block)
        total += len(block) + 4
    return "\n\n---\n\n".join(parts)

def choose_mode(user_mode: str, hits: List[Dict[str, Any]]) -> str:
    if user_mode != "auto":
        return user_mode
    for h in hits:
        if h.get("level") in ("시행규칙", "별표"):
            return "rule"
    return "law"

def ask_llm(question: str, context: str, mode: str) -> str:
    if _client is None:
        raise RuntimeError("OpenAI client not initialized")

    if mode == "rule":
        system = (
            "당신은 대한민국 최고의 EHS(환경·안전·보건) 규제 전문가다.\n"
            "반드시 제공된 컨텍스트의 근거만 사용해 답하라.\n"
            "근거 우선순위: 법률 > 시행령 > 시행규칙 > 고시/별표(표/그림/OCR).\n"
            "별표·표·그림(OCR)은 수치·치수·한계를 정확히 요약하고, OCR 특성상 오탈자 가능성은 '추가 확인사항'에 명시하라.\n"
            "형식:\n"
            "1) 요약(1~2줄)\n"
            "2) 핵심 근거(각 항목 끝에 [법령명 · 조문]만 표기. 예: [산업안전보건기준에 관한 규칙 · 별표 18])\n"
            "3) 해설(현장 적용 팁, 허용기준·치수 등 구체화)\n"
            "4) 추가 확인사항(해석상 주의, 별표/OCR 원문 재확인 포인트).\n"
            "규칙: 컨텍스트에 별표/표/그림 근거가 1개 이상 있으면 '내용이 제공되지 않았다'라고 쓰지 말고, 제공된 범위 안에서 반드시 요약하라."
        )
    else:
        system = (
            "당신은 대한민국 최고의 EHS(환경·안전·보건) 규제 전문가다.\n"
            "반드시 제공된 컨텍스트의 근거만 사용해 답하라.\n"
            "형식: 1) 요약  2) 핵심 근거(법률명·조문·핵심문구)  3) 해설  4) 추가 확인사항.\n"
            "각 근거 끝에는 [법령명 · 조문]만 표기하라(예: [산업안전보건기준에 관한 규칙 · 별표 18])."
        )

    user = f"[질문]\n{question}\n\n[검색된 근거]\n{context}\n\n위 근거만을 사용해 답하라. 근거가 부족하면 부족하다고 명시하라."
    resp = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

# ===== 요청/응답 모델 =====
class AskRequest(BaseModel):
    question: str = Field(..., description="질문 문장")
    topk: int = Field(5, ge=1, le=20, description="검색 상위 K (1~20)")
    mode: str = Field("auto", description="auto | law | rule")
    ctx_chars: int = Field(DEFAULT_CTX_CHARS, ge=1000, le=20000, description="컨텍스트 최대 길이")
    dbs: Optional[List[str]] = Field(None, description="이 요청에 사용할 DB 폴더 목록(생략 시 서버 로드 기본값 사용)")

class AskResponse(BaseModel):
    question: str
    answer: str
    mode: str
    hits: List[Dict[str, Any]]
    used_dbs: List[str]

class ReloadRequest(BaseModel):
    dbs: Optional[List[str]] = Field(None, description="로드할 DB 폴더 목록(없으면 환경변수/기본값 사용)")

class HealthResponse(BaseModel):
    status: str
    dbs: List[Dict[str, Any]]

# ===== 앱 수명주기 =====
@app.on_event("startup")
def _startup():
    global _client, _dbs
    _client = load_client()
    # 기본 DB: 환경변수에서 찾고, 없으면 vector_db 하나
    paths = _env_db_dirs()
    _dbs = load_dbs(paths)

# ===== 엔드포인트 =====
@app.get("/health", response_model=HealthResponse)
def health():
    if _client is None:
        return HealthResponse(status="not-ready", dbs=[])
    info = []
    for idx, meta, label in _dbs:
        info.append({"label": label, "size": len(meta)})
    return HealthResponse(status="ok" if _dbs else "not-ready", dbs=info)

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, request: Request):
    try:
        # 요청에 dbs가 들어오면 임시 로드해서 사용 (전역 상태는 변경하지 않음)
        used_dbs = _dbs
        used_labels = [lbl for _,_,lbl in _dbs]
        if req.dbs:
            used_dbs = load_dbs(req.dbs)
            used_labels = [lbl for _,_,lbl in used_dbs]

        qvec = embed([req.question])

        # ✅ 절대 URL 생성을 위한 base (예: "http://127.0.0.1:8000")
        static_base = str(request.base_url).rstrip("/")

        hits = search_many(used_dbs, qvec, topk=req.topk, static_base=static_base)
        hits = _prioritize_hits(hits, req.question)
        if not hits:
            raise HTTPException(404, "검색 결과가 없습니다.")

        mode = choose_mode(req.mode, hits)
        context = build_context(hits, max_chars=req.ctx_chars)
        answer = ask_llm(req.question, context, mode)
        return AskResponse(question=req.question, answer=answer, mode=mode, hits=hits, used_dbs=used_labels)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/reload-db")
def reload_db(req: ReloadRequest):
    global _dbs
    paths = req.dbs if (req and req.dbs) else _env_db_dirs()
    _dbs = load_dbs(paths)
    return {"status": "reloaded", "dbs": [{ "label": lbl, "size": len(meta)} for _,meta,lbl in _dbs]}

# ===== 로컬 실행 =====
# 맨 아래
if __name__ == "__main__":
    import uvicorn, os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)