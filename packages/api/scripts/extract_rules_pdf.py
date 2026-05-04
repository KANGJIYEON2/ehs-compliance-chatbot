#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
규칙 PDF → 본문/별표(표/그림) 추출 스크립트 (fitz 제거 / pdf2image+OCR 사용)

- 본문/별표 텍스트: pdfplumber
- 표: camelot (설치되어 있으면 사용, 실패/미설치면 건너뜀)
- 그림/스캔: pdf2image로 페이지 렌더 → pytesseract OCR
- 출력: out_dir/
    - rules_extracted.json (아이템 메타+내용)
    - images/별표XX_p{page}.png        (별표 포함 페이지의 전체 스냅샷)
    - tables/별표XX_t{idx}.md          (camelot 성공 시)

사용 예:
    py scripts\\extract_rules_pdf.py ^
      -i data\\rules\\산업안전보건기준.pdf ^
      -o extracted_rule --ocr ^
      --poppler-path "C:\\Program Files\\poppler-25.07.0\\Library\\bin"

※ 이 스크립트는 JSON에 image_path 뿐 아니라 image_url(/files/...)도 함께 기록합니다.
   FastAPI에서 app.mount("/files", StaticFiles(directory=be루트)) 로 서빙한다고 가정합니다.
"""

from __future__ import annotations
import re, json, argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

import pdfplumber

# (옵션) 표 추출
try:
    import camelot  # pip install "camelot-py[cv]"
    HAS_CAMELOT = True
except Exception:
    HAS_CAMELOT = False

# (옵션) OCR: pdf2image + pytesseract
try:
    from pdf2image import convert_from_path  # Poppler 필요
    import pytesseract                        # Tesseract 프로그램 필요
    from PIL import Image
    HAS_OCR = True
except Exception:
    HAS_OCR = False

ANNEX_HDR = re.compile(r"^\[?\s*별표\s*(\d+)\s*\]?\s*(.*)$")

# -----------------------------
# 경로 유틸: 로컬 파일 → /files/.. URL
# -----------------------------
def _to_web_url(out_path: Path, project_root: Optional[Path] = None) -> str:
    """
    로컬 파일 경로 -> /files/... 웹 URL 변환

    - project_root: FastAPI에서 StaticFiles(directory=project_root)로 마운트한 로컬 폴더
      (일반적으로 be/ 루트. 이 파일이 be/scripts/에 있을 때 기본값은 be/)
    """
    if project_root is None:
        # scripts/ 기준으로 상위가 be/ 라는 전제
        project_root = Path(__file__).resolve().parent.parent  # .../be

    try:
        rel = out_path.resolve().relative_to(project_root.resolve())
    except Exception:
        # 드라이브가 다르거나 상대 계산 실패 시 파일명만으로 비상 매핑
        rel = Path("extracted_rule") / out_path.name

    rel_posix = rel.as_posix()  # 역슬래시 → 슬래시
    return f"/files/{rel_posix}"


# -----------------------------
# 디렉터리 준비
# -----------------------------
def ensure_dirs(base: Path) -> Dict[str, Path]:
    base.mkdir(parents=True, exist_ok=True)
    img = (base / "images"); img.mkdir(exist_ok=True)
    tbl = (base / "tables"); tbl.mkdir(exist_ok=True)
    return {"base": base, "images": img, "tables": tbl}


# -----------------------------
# 별표 블록 파싱
# -----------------------------
def parse_annex_blocks(pdf_path: Path) -> List[Dict[str, Any]]:
    """pdfplumber로 라인 스캔 → '별표 n' 기준 블록 분할 + 해당 페이지 목록"""
    blocks: List[Dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        lines: List[tuple[int,str]] = []
        for pno, page in enumerate(pdf.pages, start=1):
            txt = page.extract_text() or ""
            for ln in txt.splitlines():
                s = ln.strip()
                if s:
                    lines.append((pno, s))
    cur: Optional[Dict[str,Any]] = None
    for page_no, line in lines:
        m = ANNEX_HDR.match(line)
        if m:
            if cur: blocks.append(cur)
            cur = {
                "annex_no": f"별표 {m.group(1)}",
                "annex_title": (m.group(2) or "").strip(),
                "pages": set([page_no]),
                "text": []
            }
        else:
            if cur:
                cur["text"].append(line)
                cur["pages"].add(page_no)
    if cur: blocks.append(cur)
    for b in blocks:
        b["pages"] = sorted(list(b["pages"]))
    return blocks


# -----------------------------
# 표 추출 (옵션)
# -----------------------------
def extract_tables(pdf_path: Path, pages: List[int], out_tbl_dir: Path, annex_no: str) -> List[Dict[str,Any]]:
    """Camelot로 표 추출 → Markdown 저장 (설치되어 있으면)"""
    if not HAS_CAMELOT or not pages:
        return []
    pages_str = ",".join(map(str,pages))
    try:
        tables = camelot.read_pdf(str(pdf_path), pages=pages_str, flavor="stream")
    except Exception:
        return []
    results: List[Dict[str,Any]] = []
    for ti, t in enumerate(tables, start=1):
        df = t.df
        header = "| " + " | ".join(df.iloc[0]) + " |"
        sep    = "| " + " | ".join(["---"]*df.shape[1]) + " |"
        rows   = ["| " + " | ".join(r) + " |" for _, r in df.iloc[1:].iterrows()]
        md = "\n".join([header, sep] + rows)
        fname = f"{annex_no.replace(' ','')}_t{ti}.md"
        (out_tbl_dir / fname).write_text(md, encoding="utf-8")
        results.append({
            "type":"table","annex_no":annex_no,"table_index":ti,
            "content_format":"markdown","content":md
        })
    return results


# -----------------------------
# 규칙 전체 텍스트(통짜)
# -----------------------------
def extract_rules_text(pdf_path: Path) -> List[Dict[str,Any]]:
    """규칙 전체 텍스트(통짜) 보관(후처리 파서용)"""
    with pdfplumber.open(str(pdf_path)) as pdf:
        full = []
        for page in pdf.pages:
            t = page.extract_text() or ""
            full.append(t)
    txt = "\n".join(full).strip()
    return [{"type":"rules_text","content":txt}] if txt else []


# -----------------------------
# 별표 페이지 OCR + 이미지 저장 (image_url 동시 생성)
# -----------------------------
def ocr_annex_pages(
    pdf_path: Path,
    out_img_dir: Path,
    annex_blocks: List[Dict[str,Any]],
    poppler_path: str | None,
    dpi: int,
    lang: str,
    project_root: Optional[Path] = None
) -> List[Dict[str,Any]]:
    """별표가 포함된 페이지들만 페이지 전체 이미지를 저장하고 OCR 텍스트 추출"""
    if not HAS_OCR:
        return []
    results: List[Dict[str,Any]] = []
    # 별표 포함 페이지 집합
    target_pages = sorted({p for b in annex_blocks for p in b["pages"]})
    if not target_pages:
        return results

    # annex 페이지 → annex_no 매핑
    p2annex: Dict[int,str] = {}
    for b in annex_blocks:
        for p in b["pages"]:
            p2annex[p] = b["annex_no"]

    for p in target_pages:
        imgs = convert_from_path(
            str(pdf_path),
            dpi=dpi,
            first_page=p,
            last_page=p,
            poppler_path=poppler_path
        )
        if not imgs:
            continue
        img = imgs[0]
        annex_no = p2annex.get(p, "별표미상")
        tag = annex_no.replace(" ", "")
        out_path = out_img_dir / f"{tag}_p{p}.png"
        img.save(out_path)

        # URL 생성
        image_url = _to_web_url(out_path, project_root=project_root)
        image_rel = out_path.resolve().as_posix()  # 디버깅/로그 확인용(옵션)

        try:
            text = pytesseract.image_to_string(img, lang=lang) or ""
        except Exception:
            text = ""

        results.append({
            "type": "annex_ocr",
            "annex_no": annex_no,
            "page": p,
            "image_path": str(out_path),
            "image_rel": image_rel,   # 선택 필드
            "image_url": image_url,   # ★ 프론트에서 바로 사용 가능
            "content": text.strip()
        })
    return results


# -----------------------------
# main
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Extract rules PDF (annex/tables + OCR via pdf2image)")
    ap.add_argument("-i","--input", required=True, help="규칙 PDF 경로")
    ap.add_argument("-o","--output", default="extracted_rule", help="출력 폴더")
    ap.add_argument("--ocr", action="store_true", help="별표 페이지에 OCR 수행(페이지 이미지 저장 포함)")
    ap.add_argument("--poppler-path", default=None, help="(Windows) Poppler bin 경로")
    ap.add_argument("--dpi", type=int, default=300, help="OCR 렌더링 DPI (기본 300)")
    ap.add_argument("--lang", type=str, default="kor+eng", help="Tesseract 언어 (기본 kor+eng)")
    ap.add_argument("--project-root", default=None, help="FastAPI StaticFiles 마운트 루트(be) 경로. 생략 시 자동 추정")
    args = ap.parse_args()

    in_pdf = Path(args.input).resolve()
    out = ensure_dirs(Path(args.output).resolve())
    project_root = Path(args.project_root).resolve() if args.project_root else None

    # 1) Annex 텍스트/페이지
    annex_blocks = parse_annex_blocks(in_pdf)
    items: List[Dict[str,Any]] = []
    for b in annex_blocks:
        items.append({
            "type":"annex_text",
            "annex_no": b["annex_no"],
            "annex_title": b.get("annex_title",""),
            "pages": b["pages"],
            "content": "\n".join(b.get("text",[])),
        })

    # 2) 표 (선택)
    if HAS_CAMELOT:
        for b in annex_blocks:
            items.extend(extract_tables(in_pdf, b["pages"], out["tables"], b["annex_no"]))

    # 3) 별표 페이지 OCR + 이미지 저장 (fitz 없이 페이지 전체 스냅샷)
    if args.ocr:
        ocr_items = ocr_annex_pages(
            in_pdf, out["images"], annex_blocks,
            poppler_path=args.poppler_path, dpi=args.dpi, lang=args.lang,
            project_root=project_root
        )
        items.extend(ocr_items)

    # 4) 규칙 전체 텍스트(통짜)
    items.extend(extract_rules_text(in_pdf))

    # 5) 저장
    (out["base"]/ "rules_extracted.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[OK] 추출 완료 → {out['base']}")
    print(f" - annex_text: {len([x for x in items if x.get('type')=='annex_text'])}")
    print(f" - annex_ocr : {len([x for x in items if x.get('type')=='annex_ocr'])}")
    print(f" - tables    : {len([x for x in items if x.get('type')=='table']) if HAS_CAMELOT else 0}")
    print(f" - rules_text: {len([x for x in items if x.get('type')=='rules_text'])}")
    if args.ocr:
        print(f" - OCR 사용: {'가능' if HAS_OCR else '불가 (pdf2image/pytesseract 설치 필요)'}")

if __name__ == "__main__":
    main()
