"""대시보드 통계 API"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.incident import Incident
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


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
