"""익명 위험 제보 라우터 — 제보는 인증 불필요, 관리는 관리자만"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.anonymous_report import AnonymousReport
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/anonymous-reports", tags=["anonymous-reports"])


# ── Schemas ──

class ReportCreate(BaseModel):
    site_id: str
    content: str = Field(..., min_length=5)
    location_hint: str | None = None


class ReportResponse(BaseModel):
    anonymous_token: str
    message: str = "제보가 접수되었습니다. 토큰을 저장해주세요."


class ReportStatusResponse(BaseModel):
    status: str
    risk_level: str
    ai_category: str | None = None
    admin_response: str | None = None
    created_at: str
    resolved_at: str | None = None


class AdminReportView(BaseModel):
    id: str
    site_id: str
    content: str
    location_hint: str | None
    risk_level: str
    ai_category: str | None
    status: str
    admin_response: str | None
    created_at: str
    resolved_at: str | None
    model_config = {"from_attributes": True}


class AdminActionRequest(BaseModel):
    status: str | None = None
    admin_response: str | None = None


# ── 제보자용 (인증 불필요) ──

@router.post("", response_model=ReportResponse)
def submit_report(
    req: ReportCreate,
    db: Session = Depends(get_db),
):
    """익명 위험 제보 등록 (인증 불필요)"""
    # site 존재 확인만 (company 체크 없음 — 익명이니까)
    site = db.query(Site).filter(Site.id == req.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")

    # AI 위험등급 분류
    risk_level = "warning"
    ai_category = None
    try:
        from app.main import incident_agent
        if incident_agent.is_ready:
            result = incident_agent._chat_json(
                f"""다음 익명 위험 제보를 분석하라.

제보 내용: {req.content}
{f'위치 힌트: {req.location_hint}' if req.location_hint else ''}

JSON으로 반환:
{{"risk_level": "critical|warning|improvement", "category": "사고유형(caught/fall/fire/electric 등 또는 null)"}}

- critical: 즉시 조치 필요 (생명 위험)
- warning: 1주 내 조치 필요
- improvement: 장기 개선 과제

JSON만 반환."""
            )
            risk_level = result.get("risk_level", "warning")
            ai_category = result.get("category")
    except Exception:
        pass

    report = AnonymousReport(
        site_id=req.site_id,
        content=req.content,
        location_hint=req.location_hint,
        risk_level=risk_level,
        ai_category=ai_category,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(anonymous_token=report.anonymous_token)


@router.get("/check/{token}", response_model=ReportStatusResponse)
def check_report_status(
    token: str,
    db: Session = Depends(get_db),
):
    """토큰으로 제보 처리 결과 확인 (인증 불필요)"""
    report = db.query(AnonymousReport).filter(AnonymousReport.anonymous_token == token).first()
    if not report:
        raise HTTPException(status_code=404, detail="제보를 찾을 수 없습니다")

    return ReportStatusResponse(
        status=report.status,
        risk_level=report.risk_level,
        ai_category=report.ai_category,
        admin_response=report.admin_response,
        created_at=report.created_at.isoformat(),
        resolved_at=report.resolved_at.isoformat() if report.resolved_at else None,
    )


# ── 관리자용 (인증 필요) ──

@router.get("/admin", response_model=list[AdminReportView])
def list_reports(
    status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """관리자: 제보 목록"""
    if user.role not in (UserRole.admin.value, UserRole.field_manager.value):
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    query = (
        db.query(AnonymousReport)
        .join(Site)
        .filter(Site.company_id == user.company_id)
    )
    if status:
        query = query.filter(AnonymousReport.status == status)

    reports = query.order_by(AnonymousReport.created_at.desc()).all()

    return [
        AdminReportView(
            id=r.id,
            site_id=r.site_id,
            content=r.content,
            location_hint=r.location_hint,
            risk_level=r.risk_level,
            ai_category=r.ai_category,
            status=r.status,
            admin_response=r.admin_response,
            created_at=r.created_at.isoformat(),
            resolved_at=r.resolved_at.isoformat() if r.resolved_at else None,
        )
        for r in reports
    ]


@router.patch("/admin/{report_id}", response_model=AdminReportView)
def update_report(
    report_id: str,
    req: AdminActionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """관리자: 제보에 조치 입력"""
    if user.role not in (UserRole.admin.value, UserRole.field_manager.value):
        raise HTTPException(status_code=403, detail="권한이 없습니다")

    report = db.query(AnonymousReport).filter(AnonymousReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="제보를 찾을 수 없습니다")

    site = db.query(Site).filter(Site.id == report.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="제보를 찾을 수 없습니다")

    if req.status:
        if req.status not in ("received", "reviewing", "resolved"):
            raise HTTPException(status_code=400, detail="유효하지 않은 상태")
        report.status = req.status
        if req.status == "resolved":
            report.resolved_at = datetime.utcnow()

    if req.admin_response is not None:
        report.admin_response = req.admin_response

    db.commit()
    db.refresh(report)

    return AdminReportView(
        id=report.id,
        site_id=report.site_id,
        content=report.content,
        location_hint=report.location_hint,
        risk_level=report.risk_level,
        ai_category=report.ai_category,
        status=report.status,
        admin_response=report.admin_response,
        created_at=report.created_at.isoformat(),
        resolved_at=report.resolved_at.isoformat() if report.resolved_at else None,
    )
