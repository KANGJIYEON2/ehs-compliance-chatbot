"""음성 보고 라우터 — Whisper + GPT 파싱 + 사고 자동 등록"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.site import Site
from app.models.incident import Incident, IncidentStatus
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/voice", tags=["voice"])

MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB (Whisper limit)


class TranscribeResponse(BaseModel):
    text: str


class ParseResponse(BaseModel):
    parsed: dict
    raw_text: str


class VoiceSubmitRequest(BaseModel):
    site_id: str
    incident_type: str
    severity: str
    description: str
    cause_estimate: str | None = None


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """음성 파일 → 텍스트 변환 (Whisper API)"""
    from app.main import voice_agent
    if not voice_agent.is_ready:
        raise HTTPException(status_code=503, detail="Voice Agent가 초기화되지 않았습니다")

    audio_bytes = await file.read()
    if len(audio_bytes) > MAX_AUDIO_SIZE:
        raise HTTPException(status_code=400, detail="파일이 25MB를 초과합니다")

    text = voice_agent.transcribe(audio_bytes, filename=file.filename or "audio.webm")
    return TranscribeResponse(text=text)


@router.post("/parse", response_model=ParseResponse)
def parse_text(
    text: str,
    user: User = Depends(get_current_user),
):
    """텍스트 → 구조화된 사고 보고 데이터"""
    from app.main import voice_agent
    if not voice_agent.is_ready:
        raise HTTPException(status_code=503, detail="Voice Agent가 초기화되지 않았습니다")

    parsed = voice_agent.parse_report(text)
    return ParseResponse(parsed=parsed, raw_text=text)


@router.post("/submit")
def submit_voice_report(
    req: VoiceSubmitRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """파싱된 데이터로 사고 등록"""
    site = db.query(Site).filter(Site.id == req.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")

    from datetime import datetime
    incident = Incident(
        site_id=req.site_id,
        reporter_id=user.id,
        incident_type=req.incident_type,
        severity=req.severity,
        occurred_at=datetime.utcnow(),
        description=req.description,
        cause_estimate=req.cause_estimate,
        status=IncidentStatus.reported.value,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {"incident_id": incident.id, "status": "registered"}
