"""위험성평가 자동화 라우터"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.site import Site
from app.models.risk_assessment import RiskAssessment
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/risk-assessment", tags=["risk-assessment"])


class AssessmentRequest(BaseModel):
    site_id: str
    process_name: str = Field(..., min_length=1)
    task_name: str = Field(..., min_length=1)
    task_description: str = Field(..., min_length=5)


class StatusUpdate(BaseModel):
    status: str  # draft/reviewed/approved


@router.post("")
def create_assessment(
    req: AssessmentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """위험성평가 생성 — AI가 유해위험요인 + 위험도 + 감소대책 + 법령근거 자동 분석"""
    site = db.query(Site).filter(Site.id == req.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")

    # AI 분석
    hazards = []
    risk_matrix = []
    measures = []
    legal_basis = []
    risk_level = "medium"

    try:
        from app.main import incident_agent
        if incident_agent.is_ready:
            result = incident_agent._chat_json(f"""다음 작업에 대한 위험성평가를 실시하라.

공정: {req.process_name}
작업명: {req.task_name}
작업 내용: {req.task_description}

JSON으로 반환:
{{
  "hazards": [
    {{"factor": "유해위험요인", "type": "물리적|화학적|기계적|전기적|인적", "description": "구체적 위험 설명"}}
  ],
  "risk_matrix": [
    {{"factor": "위험요인", "frequency": 1-5, "severity": 1-5, "risk_score": 빈도x강도, "level": "high|medium|low"}}
  ],
  "measures": [
    {{"factor": "위험요인", "measure": "감소대책", "type": "제거|대체|공학적|관리적|개인보호구", "priority": "high|medium|low"}}
  ],
  "legal_basis": [
    {{"law": "법령명", "article": "조문", "requirement": "요구사항 요약"}}
  ],
  "overall_risk": "high|medium|low"
}}

실제 산업현장에서 적용 가능한 구체적인 내용으로. JSON만 반환.""")

            hazards = result.get("hazards", [])
            risk_matrix = result.get("risk_matrix", [])
            measures = result.get("measures", [])
            legal_basis = result.get("legal_basis", [])
            risk_level = result.get("overall_risk", "medium")
    except Exception:
        pass

    assessment = RiskAssessment(
        site_id=req.site_id,
        created_by=user.id,
        process_name=req.process_name,
        task_name=req.task_name,
        task_description=req.task_description,
        hazards=json.dumps(hazards, ensure_ascii=False),
        risk_matrix=json.dumps(risk_matrix, ensure_ascii=False),
        measures=json.dumps(measures, ensure_ascii=False),
        legal_basis=json.dumps(legal_basis, ensure_ascii=False),
        risk_level=risk_level,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return _format(assessment)


@router.get("")
def list_assessments(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """위험성평가 목록"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)

    items = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.site_id == site_id)
        .order_by(RiskAssessment.created_at.desc())
        .all()
    )
    return [_format(a) for a in items]


@router.get("/{assessment_id}")
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """위험성평가 상세"""
    a = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404)
    site = db.query(Site).filter(Site.id == a.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)
    return _format(a)


@router.patch("/{assessment_id}/status")
def update_status(
    assessment_id: str,
    req: StatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """위험성평가 상태 변경 (draft→reviewed→approved)"""
    if req.status not in ("draft", "reviewed", "approved"):
        raise HTTPException(status_code=400, detail="유효하지 않은 상태")

    a = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
    if not a:
        raise HTTPException(status_code=404)
    site = db.query(Site).filter(Site.id == a.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)

    a.status = req.status
    a.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(a)
    return _format(a)


def _format(a: RiskAssessment) -> dict:
    return {
        "id": a.id,
        "site_id": a.site_id,
        "process_name": a.process_name,
        "task_name": a.task_name,
        "task_description": a.task_description,
        "hazards": json.loads(a.hazards),
        "risk_matrix": json.loads(a.risk_matrix),
        "measures": json.loads(a.measures),
        "legal_basis": json.loads(a.legal_basis) if a.legal_basis else [],
        "risk_level": a.risk_level,
        "status": a.status,
        "created_at": a.created_at.isoformat(),
    }
