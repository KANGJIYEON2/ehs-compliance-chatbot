"""게이미피케이션 + 위험 예측 라우터"""

import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from app.database import get_db, _is_sqlite
from app.models.user import User, UserRole
from app.models.site import Site
from app.models.incident import Incident
from app.models.gamification import SafetyPoint, SafetyQuiz, QuizResponse as QuizResponseModel, RiskScore
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


# ── 랭킹 ──

@router.get("/ranking")
def get_ranking(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """팀(부서) 단위 포인트 랭킹"""
    rows = (
        db.query(
            SafetyPoint.user_id,
            func.sum(SafetyPoint.points).label("total"),
        )
        .join(Site, SafetyPoint.site_id == Site.id)
        .filter(Site.company_id == user.company_id)
        .group_by(SafetyPoint.user_id)
        .order_by(func.sum(SafetyPoint.points).desc())
        .limit(20)
        .all()
    )

    # 사용자 이름 매핑
    from app.models.user import User as UserModel
    user_ids = [r[0] for r in rows]
    users = {u.id: u.name for u in db.query(UserModel).filter(UserModel.id.in_(user_ids)).all()}

    return [
        {"user_id": uid, "name": users.get(uid, "?"), "points": total, "rank": i + 1}
        for i, (uid, total) in enumerate(rows)
    ]


# ── 내 포인트 ──

@router.get("/my-points")
def get_my_points(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """내 포인트 히스토리"""
    total = db.query(func.sum(SafetyPoint.points)).filter(SafetyPoint.user_id == user.id).scalar() or 0
    recent = (
        db.query(SafetyPoint)
        .filter(SafetyPoint.user_id == user.id)
        .order_by(SafetyPoint.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "total": total,
        "history": [
            {"points": p.points, "reason": p.reason, "created_at": p.created_at.isoformat()}
            for p in recent
        ],
    }


# ── 포인트 적립 (시스템 내부 호출용) ──

@router.post("/award")
def award_points(
    user_id: str,
    site_id: str,
    points: int,
    reason: str,
    reference_id: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    if admin.role != UserRole.admin.value:
        raise HTTPException(status_code=403)

    sp = SafetyPoint(user_id=user_id, site_id=site_id, points=points, reason=reason, reference_id=reference_id)
    db.add(sp)
    db.commit()
    return {"status": "ok", "points": points}


# ── AI 퀴즈 ──

@router.get("/quiz/today")
def get_today_quiz(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """오늘의 안전 퀴즈 (없으면 AI 생성)"""
    today = datetime.utcnow().date()
    # 오늘 생성된 퀴즈 있는지 확인
    sites = db.query(Site).filter(Site.company_id == user.company_id).all()
    site_ids = [s.id for s in sites]

    quiz = (
        db.query(SafetyQuiz)
        .filter(
            SafetyQuiz.site_id.in_(site_ids),
            func.date(SafetyQuiz.generated_at) == str(today) if _is_sqlite
            else cast(SafetyQuiz.generated_at, Date) == today,
        )
        .first()
    )

    if not quiz:
        # AI로 퀴즈 생성
        try:
            from app.main import incident_agent
            if incident_agent.is_ready and site_ids:
                result = incident_agent._chat_json(
                    """산업안전 관련 퀴즈 1문제를 JSON으로 생성하라.
현장 작업자가 알아야 할 실용적인 내용으로.

{
  "question": "퀴즈 질문",
  "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
  "correct_index": 0,
  "explanation": "정답 해설 (1-2줄)"
}

JSON만 반환."""
                )
                quiz = SafetyQuiz(
                    site_id=site_ids[0],
                    question=result["question"],
                    options=json.dumps(result["options"], ensure_ascii=False),
                    correct_index=result["correct_index"],
                    explanation=result.get("explanation"),
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)
        except Exception:
            return {"quiz": None, "message": "퀴즈를 생성할 수 없습니다"}

    if not quiz:
        return {"quiz": None}

    # 이미 답했는지 확인
    answered = db.query(QuizResponseModel).filter(
        QuizResponseModel.quiz_id == quiz.id,
        QuizResponseModel.user_id == user.id,
    ).first()

    return {
        "quiz": {
            "id": quiz.id,
            "question": quiz.question,
            "options": json.loads(quiz.options),
            "already_answered": answered is not None,
            "correct_index": quiz.correct_index if answered else None,
            "explanation": quiz.explanation if answered else None,
        }
    }


class AnswerRequest(BaseModel):
    selected_index: int


@router.post("/quiz/{quiz_id}/answer")
def answer_quiz(
    quiz_id: str,
    req: AnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    quiz = db.query(SafetyQuiz).filter(SafetyQuiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404)

    # 중복 답변 방지
    existing = db.query(QuizResponseModel).filter(
        QuizResponseModel.quiz_id == quiz_id,
        QuizResponseModel.user_id == user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 답변했습니다")

    is_correct = req.selected_index == quiz.correct_index

    response = QuizResponseModel(
        quiz_id=quiz_id, user_id=user.id,
        selected_index=req.selected_index, is_correct=is_correct,
    )
    db.add(response)

    # 정답이면 포인트
    if is_correct:
        sites = db.query(Site).filter(Site.company_id == user.company_id).first()
        if sites:
            sp = SafetyPoint(
                user_id=user.id, site_id=sites.id,
                points=20, reason="quiz", reference_id=quiz_id,
            )
            db.add(sp)

    db.commit()

    return {
        "is_correct": is_correct,
        "correct_index": quiz.correct_index,
        "explanation": quiz.explanation,
        "points_earned": 20 if is_correct else 0,
    }


# ── 위험 예측 스코어링 ──

@router.get("/risk-scores")
def get_risk_scores(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """공정/구역별 위험도 스코어"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)

    scores = (
        db.query(RiskScore)
        .filter(RiskScore.site_id == site_id)
        .order_by(RiskScore.score.desc())
        .all()
    )

    return [
        {
            "target_type": s.target_type,
            "target_id": s.target_id,
            "target_name": s.target_name,
            "score": s.score,
            "factors": json.loads(s.factors),
            "calculated_at": s.calculated_at.isoformat(),
        }
        for s in scores
    ]


@router.post("/risk-scores/calculate")
def calculate_risk_scores(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """위험도 재계산 (AI 기반)"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)

    from app.models.master_data import Process, WorkZone

    # 공정별 사고 집계
    processes = db.query(Process).filter(Process.site_id == site_id).all()
    results = []

    for proc in processes:
        incident_count = db.query(Incident).filter(
            Incident.process_id == proc.id,
            Incident.occurred_at > datetime.utcnow() - timedelta(days=90),
        ).count()

        unresolved = db.query(Incident).filter(
            Incident.process_id == proc.id,
            Incident.status.in_(["reported", "investigating"]),
        ).count()

        # 가중 점수
        score = min(100, (incident_count * 30) + (unresolved * 25))

        factors = {
            "incident_count_90d": incident_count,
            "unresolved_count": unresolved,
        }

        # 기존 스코어 업데이트 or 생성
        existing = db.query(RiskScore).filter(
            RiskScore.site_id == site_id,
            RiskScore.target_type == "process",
            RiskScore.target_id == proc.id,
        ).first()

        if existing:
            existing.score = score
            existing.factors = json.dumps(factors)
            existing.calculated_at = datetime.utcnow()
        else:
            db.add(RiskScore(
                site_id=site_id, target_type="process",
                target_id=proc.id, target_name=proc.name,
                score=score, factors=json.dumps(factors),
            ))

        results.append({"name": proc.name, "score": score})

    db.commit()
    return {"calculated": len(results), "scores": results}
