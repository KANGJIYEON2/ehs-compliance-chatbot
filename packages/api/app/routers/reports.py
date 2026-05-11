"""월간 안전 리포트 라우터"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db, extract_year, extract_month
from app.models.user import User
from app.dependencies import get_current_user
from app.services.report_service import generate_monthly_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/monthly")
def download_monthly_report(
    year: int = Query(None),
    month: int = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """월간 안전 리포트 PDF 다운로드"""
    now = datetime.utcnow()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    # AI 요약 생성
    ai_summary = None
    try:
        from app.main import incident_agent
        if incident_agent.is_ready:
            from sqlalchemy import func
            from app.models.incident import Incident
            from app.models.site import Site

            incidents = (
                db.query(Incident)
                .join(Site)
                .filter(
                    Site.company_id == user.company_id,
                    extract_year(Incident.occurred_at) == str(year),
                    extract_month(Incident.occurred_at) == f"{month:02d}",
                )
                .all()
            )

            if incidents:
                desc_list = "\n".join(
                    f"- [{i.incident_type}] {i.description[:80]}" for i in incidents[:10]
                )
                ai_summary = incident_agent._chat(
                    f"""다음은 {year}년 {month}월 발생한 산업재해 목록이다.
월간 안전 리포트용으로 3-5줄 분석 요약을 작성하라.
주요 패턴, 반복 유형, 중점 관리 사항을 포함하라.

사고 목록:
{desc_list}""",
                    system_override="당신은 산업안전 전문가다. 월간 리포트용 간결한 분석을 한국어로 작성한다."
                )
    except Exception:
        pass

    pdf_buffer = generate_monthly_report(
        db=db,
        company_id=user.company_id,
        year=year,
        month=month,
        ai_summary=ai_summary,
    )

    filename = f"safety_report_{year}_{month:02d}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
