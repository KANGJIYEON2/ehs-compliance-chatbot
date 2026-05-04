"""AI 분석 라우터 — DB 저장 + 하루 1회 갱신"""

import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.site import Site
from app.models.incident import Incident
from app.models.ai_analysis import AIAnalysisResult
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/ai", tags=["ai-analysis"])

REFRESH_HOURS = 24  # 갱신 주기


def _get_incident_checked(incident_id: str, user: User, db: Session) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    site = db.query(Site).filter(Site.id == incident.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    return incident


def _get_cached(db: Session, incident_id: str, analysis_type: str) -> AIAnalysisResult | None:
    """캐시된 분석 결과 조회 (24시간 이내)"""
    cutoff = datetime.utcnow() - timedelta(hours=REFRESH_HOURS)
    return (
        db.query(AIAnalysisResult)
        .filter(
            AIAnalysisResult.incident_id == incident_id,
            AIAnalysisResult.analysis_type == analysis_type,
            AIAnalysisResult.created_at > cutoff,
        )
        .order_by(AIAnalysisResult.created_at.desc())
        .first()
    )


def _save_result(db: Session, incident_id: str, analysis_type: str, result: dict | list) -> None:
    """분석 결과 저장 (기존 결과 삭제 후 새로 저장)"""
    db.query(AIAnalysisResult).filter(
        AIAnalysisResult.incident_id == incident_id,
        AIAnalysisResult.analysis_type == analysis_type,
    ).delete()
    record = AIAnalysisResult(
        incident_id=incident_id,
        analysis_type=analysis_type,
        result_json=json.dumps(result, ensure_ascii=False),
    )
    db.add(record)
    db.commit()


class LawSearchRequest(BaseModel):
    incident_type: str
    description: str


# ── 저장된 분석 결과 일괄 조회 ──

@router.get("/incidents/{incident_id}/results")
def get_all_results(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """사고의 저장된 AI 분석 결과 전부 반환 (페이지 로드 시 호출)"""
    _get_incident_checked(incident_id, user, db)

    records = (
        db.query(AIAnalysisResult)
        .filter(AIAnalysisResult.incident_id == incident_id)
        .order_by(AIAnalysisResult.created_at.desc())
        .all()
    )

    results: dict = {}
    for r in records:
        if r.analysis_type not in results:
            results[r.analysis_type] = {
                "data": json.loads(r.result_json),
                "created_at": r.created_at.isoformat(),
                "is_stale": (datetime.utcnow() - r.created_at) > timedelta(hours=REFRESH_HOURS),
            }

    return results


# ── AI 원인 분석 ──

@router.post("/incidents/{incident_id}/analyze")
def analyze_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = _get_incident_checked(incident_id, user, db)

    # 캐시 확인
    cached = _get_cached(db, incident_id, "analysis")
    if cached:
        return {
            "incident_id": incident_id,
            "analysis": json.loads(cached.result_json),
            "cached": True,
            "created_at": cached.created_at.isoformat(),
        }

    from app.main import incident_agent
    if not incident_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    analysis = incident_agent.analyze_incident(
        incident_type=incident.incident_type,
        severity=incident.severity,
        description=incident.description,
        cause_estimate=incident.cause_estimate,
    )

    if "error" not in analysis:
        _save_result(db, incident_id, "analysis", analysis)

    return {"incident_id": incident_id, "analysis": analysis, "cached": False}


# ── 예방 체크리스트 ──

@router.post("/incidents/{incident_id}/checklist")
def generate_checklist(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = _get_incident_checked(incident_id, user, db)

    cached = _get_cached(db, incident_id, "checklist")
    if cached:
        return {
            "incident_id": incident_id,
            "checklist": json.loads(cached.result_json),
            "cached": True,
            "created_at": cached.created_at.isoformat(),
        }

    from app.main import incident_agent
    if not incident_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    checklist = incident_agent.generate_checklist(
        incident_type=incident.incident_type,
        description=incident.description,
    )

    if checklist:
        _save_result(db, incident_id, "checklist", checklist)

    return {"incident_id": incident_id, "checklist": checklist, "cached": False}


# ── 법령 근거 ──

@router.post("/incidents/{incident_id}/legal")
def find_legal_basis_for_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = _get_incident_checked(incident_id, user, db)

    cached = _get_cached(db, incident_id, "legal_basis")
    if cached:
        return {
            "incident_id": incident_id,
            "legal_basis": json.loads(cached.result_json),
            "cached": True,
            "created_at": cached.created_at.isoformat(),
        }

    from app.main import law_agent
    if not law_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    result = law_agent.find_legal_basis(
        incident_type=incident.incident_type,
        description=incident.description,
    )

    if "error" not in result:
        _save_result(db, incident_id, "legal_basis", result)

    return {"incident_id": incident_id, "legal_basis": result, "cached": False}


# ── 범용 법령 검색 (사고 무관) ──

@router.post("/legal-basis")
def find_legal_basis(
    req: LawSearchRequest,
    user: User = Depends(get_current_user),
):
    from app.main import law_agent
    if not law_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI Agent가 초기화되지 않았습니다")

    return law_agent.find_legal_basis(
        incident_type=req.incident_type,
        description=req.description,
    )
