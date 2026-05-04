"""사고 첨부파일 업로드/삭제 라우터"""

import uuid
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import API_PACKAGE_ROOT
from app.models.user import User
from app.models.site import Site
from app.models.incident import Incident, IncidentAttachment
from app.schemas.incident import AttachmentResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/incidents/{incident_id}/files", tags=["attachments"])

UPLOAD_DIR = API_PACKAGE_ROOT / "uploads" / "incidents"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


def _get_incident_checked(incident_id: str, user: User, db: Session) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    site = db.query(Site).filter(Site.id == incident.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사고를 찾을 수 없습니다")
    return incident


@router.post("", response_model=AttachmentResponse, status_code=201)
async def upload_file(
    incident_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    incident = _get_incident_checked(incident_id, user, db)

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"허용되지 않는 파일 형식입니다. 허용: {', '.join(ALLOWED_TYPES)}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다")

    # 저장 경로: uploads/incidents/{incident_id}/{uuid}_{filename}
    save_dir = UPLOAD_DIR / incident_id
    save_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "file").suffix
    saved_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    save_path = save_dir / saved_name

    with open(save_path, "wb") as f:
        f.write(content)

    attachment = IncidentAttachment(
        incident_id=incident_id,
        file_path=str(save_path.relative_to(API_PACKAGE_ROOT)),
        file_name=file.filename or "unknown",
        file_type=file.content_type,
        file_size=len(content),
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.delete("/{file_id}", status_code=204)
def delete_file(
    incident_id: str,
    file_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_incident_checked(incident_id, user, db)

    attachment = (
        db.query(IncidentAttachment)
        .filter(IncidentAttachment.id == file_id, IncidentAttachment.incident_id == incident_id)
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")

    # 실제 파일 삭제
    abs_path = API_PACKAGE_ROOT / attachment.file_path
    if abs_path.exists():
        os.remove(abs_path)

    db.delete(attachment)
    db.commit()
