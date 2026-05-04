"""AI 분석 라우터 — IncidentAgent + LawAgent 연동"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.site import Site
from app.models.incident import Incident
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai-analysis"])


class AnalysisResponse(BaseModel):
    incident_id: str
    analysis: dict


class LawSearchRequest(BaseModel):
    incident_type: str
    description: str


@router.post("/incidents/{incident_id}/analyze", response_model=AnalysisResponse)
def analyze_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """사고 AI 분석: 원인 분석 + 예방 체크리스트 + 재발 방지"""
    from app.main import incident_agent

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")

    site = db.query(Site).filter(Site.id == incident.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")

    if not incident_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    analysis = incident_agent.analyze_incident(
        incident_type=incident.incident_type,
        severity=incident.severity,
        description=incident.description,
        cause_estimate=incident.cause_estimate,
    )

    return AnalysisResponse(incident_id=incident_id, analysis=analysis)


@router.post("/incidents/{incident_id}/checklist")
def generate_checklist(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """사고 기반 예방 체크리스트 자동 생성"""
    from app.main import incident_agent

    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")

    site = db.query(Site).filter(Site.id == incident.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")

    if not incident_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    checklist = incident_agent.generate_checklist(
        incident_type=incident.incident_type,
        description=incident.description,
    )

    return {"incident_id": incident_id, "checklist": checklist}


@router.post("/legal-basis")
def find_legal_basis(
    req: LawSearchRequest,
    user: User = Depends(get_current_user),
):
    """사고 유형 → 관련 법령 근거 검색"""
    from app.main import law_agent

    if not law_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    return law_agent.find_legal_basis(
        incident_type=req.incident_type,
        description=req.description,
    )
