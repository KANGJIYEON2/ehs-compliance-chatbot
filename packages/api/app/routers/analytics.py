"""대시보드 통계 API"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.incident import Incident
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

TYPE_LABELS = {
    "caught": "끼임", "fall": "추락", "collision": "충돌", "electric": "감전",
    "fire": "화재", "suffocation": "질식", "falling_object": "낙하물",
    "chemical": "화학물질", "other": "기타",
}


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """전체 요약 통계"""
    base = db.query(Incident).join(Site).filter(Site.company_id == user.company_id)
    if user.role == UserRole.field_manager.value and user.site_id:
        base = base.filter(Incident.site_id == user.site_id)

    total = base.count()
    by_status = dict(
        db.query(Incident.status, func.count())
        .join(Site).filter(Site.company_id == user.company_id)
        .group_by(Incident.status).all()
    )
    by_severity = dict(
        db.query(Incident.severity, func.count())
        .join(Site).filter(Site.company_id == user.company_id)
        .group_by(Incident.severity).all()
    )

    return {
        "total": total,
        "by_status": {
            "reported": by_status.get("reported", 0),
            "investigating": by_status.get("investigating", 0),
            "resolved": by_status.get("resolved", 0),
            "monitoring": by_status.get("monitoring", 0),
        },
        "by_severity": {
            "death": by_severity.get("death", 0),
            "serious": by_severity.get("serious", 0),
            "minor": by_severity.get("minor", 0),
            "near_miss": by_severity.get("near_miss", 0),
        },
    }


@router.get("/by-type")
def get_by_type(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """사고 유형별 집계"""
    rows = (
        db.query(Incident.incident_type, func.count())
        .join(Site).filter(Site.company_id == user.company_id)
        .group_by(Incident.incident_type)
        .order_by(func.count().desc())
        .all()
    )
    return [{"type": t, "count": c} for t, c in rows]


@router.get("/by-month")
def get_by_month(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """월별 사고 추이"""
    rows = (
        db.query(
            func.strftime("%Y-%m", Incident.occurred_at).label("month"),
            func.count().label("count"),
        )
        .join(Site).filter(Site.company_id == user.company_id)
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [{"month": m, "count": c} for m, c in rows]


@router.get("/by-status")
def get_by_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """상태별 집계"""
    rows = (
        db.query(Incident.status, func.count())
        .join(Site).filter(Site.company_id == user.company_id)
        .group_by(Incident.status)
        .all()
    )
    return [{"status": s, "count": c} for s, c in rows]


@router.get("/insights")
def get_insights(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """AI 인사이트 — 위험 경고 + 전월 대비 + 반복 패턴"""
    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    base = db.query(Incident).join(Site).filter(Site.company_id == user.company_id)

    # 이번 달 / 지난 달
    this_month = base.filter(Incident.occurred_at >= this_month_start).count()
    last_month = base.filter(
        Incident.occurred_at >= last_month_start,
        Incident.occurred_at < this_month_start,
    ).count()

    # 미조치 건수
    unresolved = base.filter(Incident.status.in_(["reported", "investigating"])).count()

    # 최근 30일 유형별 최다
    recent_types = dict(
        base.filter(Incident.occurred_at >= now - timedelta(days=30))
        .with_entities(Incident.incident_type, func.count())
        .group_by(Incident.incident_type)
        .order_by(func.count().desc())
        .all()
    )
    top_type = max(recent_types, key=recent_types.get) if recent_types else None
    top_type_count = recent_types.get(top_type, 0) if top_type else 0

    # 인사이트 메시지 생성
    insights = []

    if last_month > 0 and this_month > last_month:
        pct = round((this_month - last_month) / last_month * 100)
        insights.append({
            "type": "danger",
            "title": f"이번 달 사고 전월 대비 {pct}% 증가",
            "desc": f"이번 달 {this_month}건 (전월 {last_month}건). 즉각적인 안전 점검이 필요합니다.",
        })
    elif last_month > 0 and this_month < last_month:
        pct = round((last_month - this_month) / last_month * 100)
        insights.append({
            "type": "success",
            "title": f"이번 달 사고 전월 대비 {pct}% 감소",
            "desc": f"이번 달 {this_month}건 (전월 {last_month}건). 안전 관리가 효과를 보고 있습니다.",
        })

    if unresolved > 0:
        insights.append({
            "type": "warning",
            "title": f"미조치 사고 {unresolved}건 방치 중",
            "desc": "접수/조치중 상태의 사고가 있습니다. 빠른 대응이 필요합니다.",
        })

    if top_type and top_type_count >= 2:
        insights.append({
            "type": "info",
            "title": f"최근 30일 '{TYPE_LABELS.get(top_type, top_type)}' 사고 {top_type_count}건 반복",
            "desc": f"동일 유형 사고가 반복되고 있습니다. 해당 공정의 안전 조치를 점검하세요.",
        })

    if not insights and this_month == 0:
        insights.append({
            "type": "empty",
            "title": "이번 달 등록된 사고가 없습니다",
            "desc": "사고가 없는 것이 아니라 기록이 없는 것일 수 있습니다. 아차사고도 등록해주세요.",
        })

    return {"insights": insights, "this_month": this_month, "last_month": last_month, "unresolved": unresolved}
