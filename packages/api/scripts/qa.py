#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
초미니 RAG(QA) 스크립트 - 법률/규칙 통합 버전

무엇을 하냐면:
1) 질문을 임베딩한다.
2) 하나 혹은 여러 개의 벡터DB(법률/규칙)를 동시에 검색한다.
3) 규칙/별표/표/OCR 여부에 따라 알맞은 프롬프트로 LLM에 답변을 요청한다.

필요 파일(각 DB 폴더마다):
- <db>/laws.index
- <db>/laws_meta.json
(= build_vector_db.py로 이미 만들어 둔 것; 규칙 JSON에서 만든 메타에 'type'이 있으면 표시에 활용)
"""

from __future__ import annotations
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

# ===== 설정값 =====
EMBED_MODEL = "text-embedding-3-small"  # 1536차원
CHAT_MODEL  = "gpt-4o-mini"             # 필요 시 gpt-4o 등으로 교체 가능
DEFAULT_DB_DIR = "vector_db"            # 기본 DB 경로
DEFAULT_CTX_CHARS = 6000                # 컨텍스트 길이 상한


# ===== 유틸 =====
def load_client() -> OpenAI:
    """환경변수(.env)에서 OPENAI_API_KEY 읽고 클라이언트 생성"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY 가 .env 에 없습니다.")
    # 타임아웃/리트라이 환경변수 있으면 적용(선택)
    timeout = float(os.getenv("OPENAI_TIMEOUT", "60"))
    return OpenAI(api_key=api_key, timeout=timeout)

def load_db_one(db_dir: Path) -> Tuple[faiss.Index, List[Dict[str, Any]], str]:
    """단일 DB 로드 → (index, meta, label)"""
    index_path = db_dir / "laws.index"
    meta_path  = db_dir / "laws_meta.json"
    if not index_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"❌ 벡터 DB 파일을 찾을 수 없습니다: {db_dir} (laws.index / laws_meta.json)")

    index = faiss.read_index(str(index_path))
    with meta_path.open("r", encoding="utf-8") as f:
        meta: List[Dict[str, Any]] = json.load(f)

    label = db_dir.name  # 출력용 레이블
    return index, meta, label

def load_dbs(db_dirs: List[str]) -> List[Tuple[faiss.Index, List[Dict[str, Any]], str]]:
    out: List[Tuple[faiss.Index, List[Dict[str, Any]], str]] = []
    for d in db_dirs:
        idx, meta, label = load_db_one(Path(d).resolve())
        out.append((idx, meta, label))
    return out

def embed(client: OpenAI, texts: List[str]) -> np.ndarray:
    """문장 리스트 임베딩 → (N, D) float32 ndarray"""
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    return np.array(vecs, dtype="float32")

def guess_level(law_name: str | None, article_id: str | None, src_type: str | None) -> str:
    """근거 레벨(법률/시행령/시행규칙/별표/기타) 대략 추정"""
    ln = (law_name or "")
    aid = (article_id or "")
    t = (src_type or "").lower()
    if "별표" in aid or "annex" in t:
        return "별표"
    if "규칙" in ln or "기준" in ln:
        return "시행규칙"
    if "시행령" in ln:
        return "시행령"
    if "법" in ln:
        return "법률"
    return "기타"

def search_many(
    dbs: List[Tuple[faiss.Index, List[Dict[str, Any]], str]],
    qvec: np.ndarray,
    global_topk: int = 5
) -> List[Dict[str, Any]]:
    """여러 DB에서 검색 → 거리로 통합 정렬 → 상위 global_topk"""
    all_hits: List[Dict[str, Any]] = []
    # 각 DB에서 충분히 넉넉하게 뽑은 뒤 합쳐서 상위 선별
    per_k = max(global_topk, 5)
    for index, meta, label in dbs:
        k = min(per_k, len(meta))
        D, I = index.search(qvec, k)
        for idx, dist in zip(I[0], D[0]):
            if 0 <= idx < len(meta):
                m = meta[idx]
                hit = {
                    "law_name": m.get("law_name"),
                    "article_id": m.get("article_id"),
                    "content": m.get("content", ""),
                    "type": m.get("type") or m.get("source_type"),
                    "db": label,
                    "dist": float(dist),
                }
                hit["level"] = guess_level(hit["law_name"], hit["article_id"], hit["type"])
                all_hits.append(hit)

    # 거리 오름차순 정렬 후 상위 global_topk
    all_hits.sort(key=lambda x: x["dist"])
    return all_hits[:global_topk]

def make_ref_label(h: Dict[str, Any]) -> str:
    """표시용 레퍼런스 라벨"""
    ln = h.get("law_name") or "법령/규칙"
    aid = h.get("article_id") or "-"
    typ = h.get("type")
    db  = h.get("db")
    lvl = h.get("level")
    parts = [ln, aid]
    if typ: parts.append(typ)
    if lvl: parts.append(lvl)
    if db:  parts.append(f"DB:{db}")
    return " · ".join([p for p in parts if p and p != "-"])

def build_context(hits: List[Dict[str, Any]], max_chars: int) -> str:
    """검색된 조문들을 답변용 컨텍스트 문자열로 구성(길이 제한 적용)"""
    parts: List[str] = []
    total = 0
    for h in hits:
        head = f"[{make_ref_label(h)}]"
        body = (h.get("content") or "").strip()
        block = f"{head}\n{body}"
        if total + len(block) + 4 > max_chars:
            break
        parts.append(block)
        total += len(block) + 4
    return "\n\n---\n\n".join(parts)

def choose_mode(user_mode: str, hits: List[Dict[str, Any]]) -> str:
    """auto 모드일 때 규칙 히트가 있으면 rule로 전환"""
    if user_mode != "auto":
        return user_mode
    for h in hits:
        if h.get("level") in ("시행규칙", "별표"):
            return "rule"
    return "law"

def ask_llm(client: OpenAI, question: str, context: str, mode: str) -> str:
    """LLM에게 전문가 톤으로 답변 요청 (법률/규칙 모드별 프롬프트)"""
    if mode == "rule":
        system = (
            "당신은 대한민국 최고의 EHS(환경·안전·보건) 규제 전문가다.\n"
            "반드시 제공된 컨텍스트의 근거만 사용해 답하라.\n"
            "근거 우선순위: 법률 > 시행령 > 시행규칙 > 고시/별표(표/그림/OCR).\n"
            "별표·표·그림(OCR)은 수치·치수·한계·요건을 정확히 요약하고, OCR 특성상 오탈자 가능성은 '추가 확인사항'에 명시하라.\n"
            "형식:\n"
            "1) 요약(1~2줄)\n"
            "2) 핵심 근거(각 항목에 [법령·조문/별표 라벨]과 핵심 문구)\n"
            "3) 해설(현장 적용 팁, 허용기준·치수 등 구체화)\n"
            "4) 추가 확인사항(해석상 주의, 별표/OCR 원문 재확인 포인트)."
        )
    else:
        system = (
            "당신은 대한민국 최고의 EHS(환경·안전·보건) 규제 전문가다.\n"
            "반드시 제공된 컨텍스트의 근거만 사용해 답하라.\n"
            "형식: 1) 요약  2) 핵심 근거(법률명·조문·핵심문구)  3) 해설  4) 추가 확인사항."
        )

    user = (
        f"[질문]\n{question}\n\n"
        f"[검색된 근거]\n{context}\n\n"
        "위 근거만을 사용해 답하라. 근거가 부족하면 부족하다고 명시하라.\n"
        "각 근거 끝에는 대괄호로 제공된 라벨([…])을 그대로 표기하라."
    )

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user",   "content": user}],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


# ===== 실행 엔트리 =====
def main():
    ap = argparse.ArgumentParser(description="Mini Law/Rule RAG (통합 버전)")
    ap.add_argument("-q", "--query", required=True, help="질문 문장")
    ap.add_argument(
        "-d", "--db",
        action="append",
        default=[DEFAULT_DB_DIR],
        help="벡터DB 폴더 (여러 번 지정 가능). 예: -d vector_db_law -d vector_db_rule"
    )
    ap.add_argument("-k", "--topk", type=int, default=5, help="검색 상위 K (기본: 5, 전체 통합 Top-K)")
    ap.add_argument("--mode", choices=["auto", "law", "rule"], default="auto", help="프롬프트 모드 (기본: auto)")
    ap.add_argument("--ctx-chars", type=int, default=DEFAULT_CTX_CHARS, help="컨텍스트 최대 길이(문자)")
    args = ap.parse_args()

    client = load_client()
    dbs = load_dbs(args.db)

    # 1) 질문 → 임베딩
    qvec = embed(client, [args.query])

    # 2) 통합 검색
    hits = search_many(dbs, qvec, global_topk=args.topk)
    if not hits:
        print("⚠️ 검색 결과가 없습니다. 질문을 바꾸거나 벡터DB를 확인하세요.")
        return

    # 3) 모드 결정 & 컨텍스트 구성
    mode = choose_mode(args.mode, hits)
    context = build_context(hits, max_chars=args.ctx_chars)

    # 4) LLM 답변
    answer = ask_llm(client, args.query, context, mode)

    # 보기 좋은 출력
    print("\n[Query]")
    print(args.query)

    print("\n[Top-K 근거]")
    for i, h in enumerate(hits, 1):
        print(f"{i}. {make_ref_label(h)}  (L2={h['dist']:.4f})")

    print(f"\n[Mode] {mode}")
    print("\n[Answer]\n")
    print(answer)


if __name__ == "__main__":
    main()
