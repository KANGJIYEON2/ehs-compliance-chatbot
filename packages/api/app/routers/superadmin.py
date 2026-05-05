"""SuperAdmin 라우터 — 플랫폼 전체 관리"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.site import Site
from app.models.incident import Incident
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/superadmin", tags=["superadmin"])


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.superadmin.value:
        raise HTTPException(status_code=403, detail="SuperAdmin 권한이 필요합니다")
    return user


@router.get("/companies")
def list_all_companies(
    db: Session = Depends(get_db),
    user: User = Depends(require_superadmin),
):
    """전체 기업 목록 + 통계"""
    companies = db.query(Company).all()
    result = []
    for c in companies:
        user_count = db.query(User).filter(User.company_id == c.id).count()
        site_count = db.query(Site).filter(Site.company_id == c.id).count()
        incident_count = (
            db.query(Incident)
            .join(Site)
            .filter(Site.company_id == c.id)
            .count()
        )
        result.append({
            "id": c.id,
            "name": c.name,
            "business_number": c.business_number,
            "created_at": c.created_at.isoformat(),
            "users": user_count,
            "sites": site_count,
            "incidents": incident_count,
        })
    return result


@router.get("/stats")
def platform_stats(
    db: Session = Depends(get_db),
    user: User = Depends(require_superadmin),
):
    """플랫폼 전체 통계"""
    return {
        "total_companies": db.query(Company).count(),
        "total_users": db.query(User).count(),
        "total_sites": db.query(Site).count(),
        "total_incidents": db.query(Incident).count(),
        "users_by_role": dict(
            db.query(User.role, func.count()).group_by(User.role).all()
        ),
    }


@router.get("/companies/{company_id}")
def get_company_detail(
    company_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_superadmin),
):
    """기업 상세 정보"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="기업을 찾을 수 없습니다")

    users = db.query(User).filter(User.company_id == company_id).all()
    sites = db.query(Site).filter(Site.company_id == company_id).all()
    incidents = (
        db.query(Incident).join(Site).filter(Site.company_id == company_id)
        .order_by(Incident.created_at.desc()).limit(10).all()
    )

    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "business_number": company.business_number,
            "created_at": company.created_at.isoformat(),
        },
        "users": [
            {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
            for u in users
        ],
        "sites": [
            {"id": s.id, "name": s.name, "address": s.address}
            for s in sites
        ],
        "recent_incidents": [
            {
                "id": i.id, "incident_type": i.incident_type,
                "severity": i.severity, "status": i.status,
                "description": i.description[:100],
                "occurred_at": i.occurred_at.isoformat(),
            }
            for i in incidents
        ],
    }
