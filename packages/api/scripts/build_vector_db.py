#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
법령/규칙 → Embedding → FAISS Vector DB 구축 (통합 스크립트)
- 입력이 '폴더'면: *.txt를 조문 단위로 파싱(법률 모드)
- 입력이 'JSON 파일'이면: extract_rules_pdf.py 산출물(rules_extracted.json) 기반(규칙/별표/OCR 모드)
- .env에서 OPENAI_API_KEY 읽음

사용 예)
# 1) 법률(폴더의 TXT들)
py scripts/build_vector_db.py -i data/laws -o vector_db_law

# 2) 규칙(JSON: extract_rules_pdf.py 산출물)
py scripts/build_vector_db.py -i extracted_rule/rules_extracted.json -o vector_db_rule --law-name "산업안전보건기준에 관한 규칙"
"""

from __future__ import annotations
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Any

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI

# ───────────── Load .env ─────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file")

# ───────────── Config ─────────────
EMBED_MODEL  = os.getenv("EMBED_MODEL", "text-embedding-3-small")  # 1536 차원
CHUNK_SIZE   = int(os.getenv("CHUNK_SIZE", "500"))                 # 문자 단위 청크 사이즈(법률 TXT용)
EMBED_BATCH  = int(os.getenv("EMBED_BATCH", "256"))                # 임베딩 배치 크기
RULE_CHUNK_MAX = int(os.getenv("RULE_CHUNK_MAX", "700"))           # 규칙 JSON 청킹 상한

# ───────────── OpenAI ─────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ───────────── Embedding ─────────────
def embed_texts(texts: List[str]) -> List[List[float]]:
    """텍스트 리스트 → OpenAI Embedding (배치 처리, 빈 문자열 제거)"""
    vectors: List[List[float]] = []
    buf: List[str] = []
    for t in texts:
        if t and t.strip():
            buf.append(t.strip())
        if len(buf) >= EMBED_BATCH:
            resp = client.embeddings.create(model=EMBED_MODEL, input=buf)
            vectors.extend([d.embedding for d in resp.data])
            buf = []
    if buf:
        resp = client.embeddings.create(model=EMBED_MODEL, input=buf)
        vectors.extend([d.embedding for d in resp.data])
    return vectors

# ───────────── 모드 A: 법률 TXT 폴더 ─────────────
# ex) "제1조 목적", "제 1 조 (목적)", "제1조의2" (같은 줄 본문 포함)
ART_HDR = re.compile(r'^(제\s*\d+\s*조(?:의\s*\d+)?)(.*)$')

def split_articles(text: str, law_name: str) -> List[Dict]:
    """법령 텍스트를 '조문 단위'로 쪼갬 (같은 줄 본문 포함)"""
    articles: List[Dict] = []
    current: Dict | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = ART_HDR.match(line)
        if m:  # 새로운 조문 시작
            if current:
                current["content"] = current["content"].strip()
                if current["content"]:
                    articles.append(current)
            same_line = m.group(2).strip() if m.group(2) else ""
            current = {
                "law_name": law_name,
                "article_id": m.group(1).strip(),
                "content": same_line
            }
        elif current:
            current["content"] = (current["content"] + " " + line).strip() if current["content"] else line
    if current:
        current["content"] = current["content"].strip()
        if current["content"]:
            articles.append(current)
    return articles

def chunk_article(article: Dict, chunk_size: int = CHUNK_SIZE) -> List[Dict]:
    """조문 content를 chunk_size 기준으로 쪼갬"""
    text = (article.get("content") or "").strip()
    if not text:
        return []
    chunks: List[Dict] = []
    for i in range(0, len(text), chunk_size):
        seg = text[i:i+chunk_size].strip()
        if not seg:
            continue
        chunks.append({
            "law_name": article["law_name"],
            "article_id": article["article_id"],
            "content": seg
        })
    return chunks

def build_from_txt_dir(in_dir: Path) -> Tuple[List[Dict], List[str]]:
    """폴더 내 *.txt → 조문청킹 → (메타, 콘텐츠목록)"""
    txt_files = sorted(list(in_dir.glob("*.txt")))
    print(f"[INFO] TXT 파일 수: {len(txt_files)}  (경로: {in_dir})")
    for f in txt_files[:10]:
        print(f"  - {f.name}")
    if not txt_files:
        raise RuntimeError("⚠️ TXT 파일이 없습니다. -i 경로를 확인하세요.")

    docs: List[Dict] = []
    for txt_file in txt_files:
        try:
            text = txt_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = txt_file.read_text(encoding="utf-8", errors="ignore")
        law_name = txt_file.stem
        articles = split_articles(text, law_name)
        for art in articles:
            docs.extend(chunk_article(art, CHUNK_SIZE))

    contents = [d["content"] for d in docs if d.get("content") and d["content"].strip()]
    if not contents:
        raise RuntimeError("⚠️ 비어있는 청크만 감지되었습니다. 파싱 로직 또는 원본 TXT 확인.")
    return docs, contents

# ───────────── 모드 B: 규칙 JSON(rules_extracted.json) ─────────────
def chunk_text_blocks(s: str, max_len: int = RULE_CHUNK_MAX) -> List[str]:
    s = (s or "").strip()
    if not s:
        return []
    chunks: List[str] = []
    for para in s.split("\n"):
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_len:
            chunks.append(para)
        else:
            for i in range(0, len(para), max_len):
                chunks.append(para[i:i+max_len])
    return chunks

def build_from_rules_json(json_path: Path, law_name_fallback: str) -> Tuple[List[Dict], List[str]]:
    """rules_extracted.json → 타입별 청킹/요약 → (메타, 콘텐츠목록)"""
    items: List[Dict[str, Any]] = json.loads(json_path.read_text(encoding="utf-8"))
    docs: List[Dict] = []
    contents: List[str] = []

    # 규칙명 기본값 (필요 시 CLI --law-name으로 지정)
    LAW_NAME = law_name_fallback

    for it in items:
        t = it.get("type")

        if t == "annex_text":
            for chunk in chunk_text_blocks(it.get("content", "")):
                docs.append({
                    "law_name": LAW_NAME,
                    "section_type": "annex_text",
                    "annex_no": it.get("annex_no"),
                    "annex_title": it.get("annex_title", ""),
                    "content": chunk
                })
                contents.append(chunk)

        elif t == "table":
            md = (it.get("content") or "").strip()
            if md:
                # 1) 원문 markdown
                docs.append({
                    "law_name": LAW_NAME,
                    "section_type": "table",
                    "annex_no": it.get("annex_no"),
                    "content_format": "markdown",
                    "content": md
                })
                contents.append(md)
                # 2) 간단 요약(검색-friendly)
                lines = [ln.strip() for ln in md.splitlines() if ln.strip() and not ln.startswith("| ---")]
                if lines:
                    summary = " / ".join(lines[:6])
                    docs.append({
                        "law_name": LAW_NAME,
                        "section_type": "table_summary",
                        "annex_no": it.get("annex_no"),
                        "content_format": "text",
                        "content": summary
                    })
                    contents.append(summary)

        elif t == "annex_ocr":
            txt = (it.get("content") or "").strip()
            if txt:
                docs.append({
                    "law_name": LAW_NAME,
                    "section_type": "annex_ocr",
                    "annex_no": it.get("annex_no"),
                    "page": it.get("page"),
                    "content": txt
                })
                contents.append(txt)

        elif t == "ocr_page":
            txt = (it.get("content") or "").strip()
            if txt:
                docs.append({
                    "law_name": LAW_NAME,
                    "section_type": "ocr_page",
                    "page": it.get("page"),
                    "content": txt
                })
                contents.append(txt)

        elif t == "rules_text":
            for chunk in chunk_text_blocks(it.get("content", "")):
                docs.append({
                    "law_name": LAW_NAME,
                    "section_type": "rules_text",
                    "content": chunk
                })
                contents.append(chunk)

        # 그 외 타입은 스킵

    if not contents:
        raise RuntimeError("⚠️ 규칙 JSON에서 임베딩할 내용이 비어 있습니다. 추출 결과를 확인하세요.")
    return docs, contents

# ───────────── 공통: 저장 ─────────────
def save_faiss_index_and_meta(vectors: List[List[float]], docs: List[Dict], out_dir: Path) -> None:
    if not vectors:
        raise RuntimeError("⚠️ 임베딩 결과가 비어 있습니다.")
    X = np.array(vectors, dtype="float32")
    dim = X.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(X)

    out_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_dir / "laws.index"))
    (out_dir / "laws_meta.json").write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] 벡터 DB 저장 완료 → {out_dir}")
    print(f"     - index: {out_dir / 'laws.index'}")
    print(f"     - meta : {out_dir / 'laws_meta.json'}")
    print(f"     - dim  : {dim}, vectors: {len(vectors)}, docs: {len(docs)}")

# ───────────── CLI ─────────────
def main():
    p = argparse.ArgumentParser(description="(법률 TXT or 규칙 JSON) → Embedding → FAISS Vector DB")
    p.add_argument("-i", "--input", type=str, required=True, help="입력 경로: 폴더(*.txt) 또는 rules_extracted.json")
    p.add_argument("-o", "--output", type=str, default="vector_db", help="출력 폴더")
    p.add_argument("--law-name", type=str, default="산업안전보건기준에 관한 규칙",
                   help="규칙 JSON 처리 시 메타에 기록할 규칙명(기본: 산업안전보건기준에 관한 규칙)")
    args = p.parse_args()

    in_path = Path(args.input).resolve()
    out_dir = Path(args.output).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 입력 유형 판별
    if in_path.is_dir():
        # 모드 A: 폴더 내 TXT (법률)
        docs, contents = build_from_txt_dir(in_path)

        # 임베딩
        vectors = embed_texts(contents)

        # TXT 파이프라인은 '사용된 docs' 슬라이스 불필요(이미 contents와 1:1)
        save_faiss_index_and_meta(vectors, docs, out_dir)

    elif in_path.is_file() and in_path.suffix.lower() == ".json":
        # 모드 B: 규칙 JSON
        docs, contents = build_from_rules_json(in_path, args.law_name)

        vectors = embed_texts(contents)
        save_faiss_index_and_meta(vectors, docs, out_dir)

    else:
        raise SystemExit("❌ 입력 경로가 폴더도 아니고 .json 파일도 아닙니다. -i 옵션을 확인하세요.")

if __name__ == "__main__":
    main()
