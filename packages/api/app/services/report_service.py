"""월간 안전 리포트 PDF 생성 서비스"""

from __future__ import annotations

import io
import os
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.site import Site

# 한글 폰트 등록 (시스템 폰트 사용)
_FONT_REGISTERED = False

def _register_font():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",        # Windows 맑은 고딕
        "C:/Windows/Fonts/gulim.ttc",          # Windows 굴림
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("Korean", fp))
                _FONT_REGISTERED = True
                return
            except Exception:
                continue
    # fallback — 폰트 없으면 기본 폰트 사용
    _FONT_REGISTERED = True


TYPE_LABELS = {
    "caught": "끼임", "fall": "추락", "collision": "충돌", "electric": "감전",
    "fire": "화재", "suffocation": "질식", "falling_object": "낙하물",
    "chemical": "화학물질", "other": "기타",
}
SEVERITY_LABELS = {
    "death": "사망", "serious": "중상", "minor": "경상", "near_miss": "아차사고",
}
STATUS_LABELS = {
    "reported": "접수", "investigating": "조치중", "resolved": "조치완료", "monitoring": "재발관리",
}


def generate_monthly_report(
    db: Session,
    company_id: str,
    year: int,
    month: int,
    ai_summary: str | None = None,
) -> io.BytesIO:
    """월간 안전 리포트 PDF 생성"""
    _register_font()

    font_name = "Korean" if _FONT_REGISTERED else "Helvetica"

    # 데이터 집계
    base_query = (
        db.query(Incident)
        .join(Site)
        .filter(
            Site.company_id == company_id,
            func.strftime("%Y", Incident.occurred_at) == str(year),
            func.strftime("%m", Incident.occurred_at) == f"{month:02d}",
        )
    )

    total = base_query.count()
    by_type = dict(
        base_query.with_entities(Incident.incident_type, func.count())
        .group_by(Incident.incident_type).all()
    )
    by_severity = dict(
        base_query.with_entities(Incident.severity, func.count())
        .group_by(Incident.severity).all()
    )
    by_status = dict(
        base_query.with_entities(Incident.status, func.count())
        .group_by(Incident.status).all()
    )

    # 이전 달 비교
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_total = (
        db.query(Incident)
        .join(Site)
        .filter(
            Site.company_id == company_id,
            func.strftime("%Y", Incident.occurred_at) == str(prev_year),
            func.strftime("%m", Incident.occurred_at) == f"{prev_month:02d}",
        )
        .count()
    )

    # PDF 생성
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title_KR", parent=styles["Title"], fontName=font_name, fontSize=18)
    heading_style = ParagraphStyle("H2_KR", parent=styles["Heading2"], fontName=font_name, fontSize=14)
    body_style = ParagraphStyle("Body_KR", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=14)
    small_style = ParagraphStyle("Small_KR", parent=styles["Normal"], fontName=font_name, fontSize=8, textColor=colors.grey)

    elements = []

    # 제목
    elements.append(Paragraph(f"{year}년 {month}월 안전 리포트", title_style))
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}", small_style))
    elements.append(Spacer(1, 3*mm))
    elements.append(HRFlowable(width="100%", color=colors.grey))
    elements.append(Spacer(1, 8*mm))

    # 요약
    elements.append(Paragraph("1. 월간 요약", heading_style))
    elements.append(Spacer(1, 3*mm))

    diff = total - prev_total
    diff_text = f"(전월 대비 {'+'if diff>0 else ''}{diff}건)" if prev_total > 0 else ""

    summary_data = [
        ["항목", "건수"],
        ["이번 달 사고/아차사고", f"{total}건 {diff_text}"],
        ["전월 사고/아차사고", f"{prev_total}건"],
    ]
    t = Table(summary_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    # 유형별 현황
    elements.append(Paragraph("2. 사고 유형별 현황", heading_style))
    elements.append(Spacer(1, 3*mm))

    type_data = [["사고 유형", "건수"]]
    for k, v in sorted(by_type.items(), key=lambda x: -x[1]):
        type_data.append([TYPE_LABELS.get(k, k), f"{v}건"])
    if len(type_data) == 1:
        type_data.append(["(해당 없음)", "0건"])

    t = Table(type_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    # 심각도별
    elements.append(Paragraph("3. 심각도별 현황", heading_style))
    elements.append(Spacer(1, 3*mm))

    sev_data = [["심각도", "건수"]]
    for k in ["death", "serious", "minor", "near_miss"]:
        v = by_severity.get(k, 0)
        if v > 0:
            sev_data.append([SEVERITY_LABELS[k], f"{v}건"])
    if len(sev_data) == 1:
        sev_data.append(["(해당 없음)", "0건"])

    t = Table(sev_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 8*mm))

    # 상태별
    elements.append(Paragraph("4. 조치 현황", heading_style))
    elements.append(Spacer(1, 3*mm))

    status_data = [["상태", "건수"]]
    for k in ["reported", "investigating", "resolved", "monitoring"]:
        v = by_status.get(k, 0)
        if v > 0:
            status_data.append([STATUS_LABELS[k], f"{v}건"])
    if len(status_data) == 1:
        status_data.append(["(해당 없음)", "0건"])

    unresolved = by_status.get("reported", 0) + by_status.get("investigating", 0)

    t = Table(status_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)

    if unresolved > 0:
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph(
            f"* 미조치 항목 {unresolved}건 — 조속한 조치가 필요합니다.",
            ParagraphStyle("Warning", parent=body_style, textColor=colors.red),
        ))

    elements.append(Spacer(1, 8*mm))

    # AI 요약
    if ai_summary:
        elements.append(Paragraph("5. AI 분석 요약", heading_style))
        elements.append(Spacer(1, 3*mm))
        for line in ai_summary.split("\n"):
            if line.strip():
                elements.append(Paragraph(line.strip(), body_style))
                elements.append(Spacer(1, 2*mm))
        elements.append(Spacer(1, 5*mm))

    # 푸터
    elements.append(HRFlowable(width="100%", color=colors.grey))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        "본 리포트는 EHS 리스크 관리 플랫폼에서 자동 생성되었습니다.",
        small_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
