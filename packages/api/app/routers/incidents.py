"""사고/아차사고 CRUD 라우터"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.incident import Incident, IncidentType, Severity, IncidentStatus
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

VALID_TYPES = {e.value for e in IncidentType}
VALID_SEVERITIES = {e.value for e in Severity}
VALID_STATUSES = {e.value for e in IncidentStatus}


def _check_site_belongs_to_company(site_id: str, user: User, db: Session) -> Site:
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")
    if user.role == UserRole.field_manager.value and user.site_id and user.site_id != site.id:
        raise HTTPException(status_code=403, detail="해당 사업장에 대한 권한이 없습니다")
    return site


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    site_id: str | None = None,
    incident_type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = (
        db.query(Incident)
        .join(Site)
        .filter(Site.company_id == user.company_id)
    )

    # field_manager는 본인 사업장만
    if user.role == UserRole.field_manager.value and user.site_id:
        query = query.filter(Incident.site_id == user.site_id)

    if site_id:
        query = query.filter(Incident.site_id == site_id)
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)

    total = query.count()
    items = (
        query.options(joinedload(Incident.attachments))
        .order_by(Incident.occurred_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return IncidentListResponse(items=items, total=total, page=page, size=size)


@router.post("", response_model=IncidentResponse, status_code=201)
def create_incident(
    req: IncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _check_site_belongs_to_company(req.site_id, user, db)

    if req.incident_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 사고 유형: {req.incident_type}")
    if req.severity not in VALID_SEVERITIES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 심각도: {req.severity}")

    incident = Incident(
        site_id=req.site_id,
        reporter_id=user.id,
        incident_type=req.incident_type,
        severity=req.severity,
        occurred_at=req.occurred_at,
        work_zone_id=req.work_zone_id,
        process_id=req.process_id,
        equipment_id=req.equipment_id,
        department_id=req.department_id,
        description=req.description,
        cause_estimate=req.cause_estimate,
        action_taken=req.action_taken,
        status=IncidentStatus.reported.value,
    )
    db.add(incident)

    # 관리자에게 알림
    from app.routers.notifications import create_notification
    admins = db.query(User).filter(User.company_id == user.company_id, User.role == "admin").all()
    for admin in admins:
        if admin.id != user.id:
            create_notification(
                db, admin.id, "incident_new",
                f"새 사고 접수: {req.incident_type}",
                req.description[:100],
                f"/dashboard/incidents/{incident.id}",
            )

    db.commit()
    db.refresh(incident)
    return incident


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = (
        db.query(Incident)
        .options(joinedload(Incident.attachments))
        .filter(Incident.id == incident_id)
        .first()
    )
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    _check_site_belongs_to_company(incident.site_id, user, db)
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    req: IncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    _check_site_belongs_to_company(incident.site_id, user, db)

    update_data = req.model_dump(exclude_unset=True)

    if "incident_type" in update_data and update_data["incident_type"] not in VALID_TYPES:
        raise HTTPException(status_code=400, detail="유효하지 않은 사고 유형")
    if "severity" in update_data and update_data["severity"] not in VALID_SEVERITIES:
        raise HTTPException(status_code=400, detail="유효하지 않은 심각도")
    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="유효하지 않은 상태")

    # 담당자 배정 시 알림
    if "assignee_id" in update_data and update_data["assignee_id"]:
        # cross-tenant 차단: 배정 대상이 같은 회사 사용자인지 검증
        assignee = db.query(User).filter(
            User.id == update_data["assignee_id"],
            User.company_id == user.company_id,
        ).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="담당자를 찾을 수 없습니다")
        from app.routers.notifications import create_notification
        create_notification(
            db, update_data["assignee_id"], "incident_assigned",
            "사고 조치가 배정되었습니다",
            f"{incident.description[:80]}",
            f"/dashboard/incidents/{incident_id}",
        )

    for key, value in update_data.items():
        setattr(incident, key, value)

    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != UserRole.admin.value:
        raise HTTPException(status_code=403, detail="관리자만 삭제할 수 있습니다")

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    _check_site_belongs_to_company(incident.site_id, user, db)

    db.delete(incident)
    db.commit()
