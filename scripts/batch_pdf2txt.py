#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
data/laws 폴더의 모든 .pdf를 .txt로 변환합니다.
- pdfminer.six 사용 (PyMuPDF 미사용)
- 파일명은 그대로 두고 확장자만 .txt로 변경
- 간단 전처리 + 목차(본문 없는 조문목록) 자동 제거
사용법:
    python scripts/batch_pdf2txt.py --input data/laws --output data/laws --overwrite
    # Windows PowerShell에서 글자 깨지면 --bom 옵션을 쓰세요:
    # python scripts/batch_pdf2txt.py -i data/laws -o data/laws --overwrite --bom
"""

import re
import sys
import argparse
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

# ───────────── 전처리 ─────────────
def clean_text(raw: str) -> str:
    """법령 PDF에서 흔한 잡개행/공백 정리"""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")

    # 페이지 번호 한 줄(예: - 12 -) 또는 숫자만 라인 제거
    lines = text.split("\n")
    cleaned = []
    for ln in lines:
        if re.fullmatch(r"\s*-?\s*\d+\s*-?\s*", ln):
            continue
        cleaned.append(ln)
    text = "\n".join(cleaned)

    # 연속 공백/개행 정리
    text = re.sub(r"[ \t]+", " ", text)       # 연속 공백 하나로
    text = re.sub(r"\n{3,}", "\n\n", text)    # 과도 개행 축소

    # 조문 헤더 가독성(제1조(…)) 주변 개행 보장
    text = re.sub(r"\n?(제\s*\d+\s*조(?:의\s*\d+)?\s*\(.*?\))", r"\n\1", text)
    text = re.sub(r"(제\s*\d+\s*조(?:의\s*\d+)?\s*\(.*?\))", r"\1\n", text)
    return text.strip() + "\n"

# ───────────── 목차(조문목록) 제거 ─────────────
ART_HDR = re.compile(r'^제\s*\d+\s*조(?:의\s*\d+)?\s*\(.*?\)\s*$')   # 제4조의2(...) 대응
CHAPTER = re.compile(r'^제\s*\d+\s*장[^\n]*$')

def drop_toc_and_keep_real_articles(text: str) -> str:
    """
    조문 헤더만 나열된 '목차' 블록은 버리고,
    '헤더 + 본문'이 있는 진짜 조문만 남김. 장/절 제목은 보존.
    """
    lines = text.splitlines()
    out = []
    i, kept, dropped = 0, 0, 0

    # 프리앰블(법명, 시행일 등) 먼저 복사: 첫 조문 헤더 전까지
    while i < len(lines) and not ART_HDR.match(lines[i]):
        out.append(lines[i])
        i += 1

    # 조문 단위로 스캔
    while i < len(lines):
        if ART_HDR.match(lines[i]):
            head = lines[i].strip()
            j = i + 1
            # 다음 조문 헤더 또는 EOF 전까지 본문 수집
            body = []
            while j < len(lines) and not ART_HDR.match(lines[j]):
                body.append(lines[j])
                j += 1

            # 본문에 실내용이 있는지 판단(빈 줄만/공백만이면 목차로 간주)
            body_txt = "\n".join([b for b in body]).strip()

            # 장/절 표제는 본문으로 오인하지 않도록 처리
            # (있으면 out로 먼저 내보내고, 본문 판정에서 제외)
            body_lines = body_txt.split("\n") if body_txt else []
            moved = []
            rest = []
            for bl in body_lines:
                if CHAPTER.match(bl.strip()):
                    moved.append(bl.strip())
                else:
                    rest.append(bl)
            if moved:
                out.extend(moved)
            real_body = "\n".join(rest).strip()

            # '본문 없음'이면 목차로 판단하여 버림
            # (※ 숫자/항목표 "①②1." 같은 것도 본문으로 인정)
            has_content = bool(real_body) and len(real_body.replace(" ", "")) >= 5
            if has_content:
                # 조문 기록
                out.append(head)
                out.append(real_body)
                out.append("")  # 조문간 빈 줄
                kept += 1
            else:
                dropped += 1

            i = j
            continue

        # 조문 외 라인(예: 장 표제 등)
        out.append(lines[i])
        i += 1

    # 마무리: 여분 개행 정리
    cleaned = "\n".join(out)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip() + "\n"
    # 처리 로그(참고용)
    # print(f"[INFO] articles kept={kept}, toc_dropped={dropped}")
    return cleaned

# ───────────── PDF → TXT ─────────────
def pdf_to_txt(pdf_path: Path, txt_path: Path, encoding: str = "utf-8") -> None:
    """단일 PDF → TXT (pdfminer) + 전처리 + 목차 제거"""
    try:
        laparams = LAParams()  # 필요 시 word_margin, line_margin, boxes_flow 조절
        raw = extract_text(str(pdf_path), laparams=laparams) or ""
    except Exception as e:
        print(f"[FAIL] {pdf_path.name}: PDF 추출 실패 ({e})")
        return

    text = clean_text(raw)
    text = drop_toc_and_keep_real_articles(text)

    txt_path.write_text(text, encoding=encoding)
    print(f"[OK]  {pdf_path.name}  ->  {txt_path.name}  ({len(text):,} chars)")

# ───────────── CLI ─────────────
def main():
    p = argparse.ArgumentParser(description="Batch convert PDFs to TXT for RAG (pdfminer, TOC removed)")
    p.add_argument("--input", "-i", type=str, default="data/laws", help="PDF 입력 폴더")
    p.add_argument("--output", "-o", type=str, default=None, help="TXT 출력 폴더(기본=입력과 동일)")
    p.add_argument("--overwrite", action="store_true", help="기존 TXT 덮어쓰기")
    p.add_argument("--bom", action="store_true", help="UTF-8 BOM으로 저장(Win PS5 글깨짐 방지)")
    args = p.parse_args()

    in_dir = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve() if args.output else in_dir

    if not in_dir.exists():
        print(f"입력 폴더가 없습니다: {in_dir}")
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted([p for p in in_dir.glob("*.pdf") if p.is_file()])
    if not pdfs:
        print(f"PDF가 없습니다: {in_dir}")
        sys.exit(0)

    print(f"입력: {in_dir}")
    print(f"출력: {out_dir}")
    print(f"대상 PDF: {len(pdfs)}개\n")

    enc = "utf-8-sig" if args.bom else "utf-8"

    for pdf in pdfs:
        txt = out_dir / (pdf.stem + ".txt")
        if txt.exists() and not args.overwrite:
            print(f"[SKIP] {txt.name} (이미 존재, --overwrite로 덮어쓰기 가능)")
            continue
        pdf_to_txt(pdf, txt, encoding=enc)

    print("\n완료!")

if __name__ == "__main__":
    main()
