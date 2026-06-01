"""다국어 안전 안내 + QR 라우터"""

import io
from datetime import datetime

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.user import User
from app.models.site import Site
from app.models.safety_guide import SafetyGuide, SafetyGuideTranslation, TrainingRecord
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/safety-guide", tags=["safety-guide"])

SUPPORTED_LANGS = {"ko": "한국어", "vi": "베트남어", "en": "영어", "km": "캄보디아어", "ne": "네팔어", "my": "미얀마어"}


class GuideCreate(BaseModel):
    site_id: str
    target_type: str = Field(..., description="equipment or work_zone")
    target_id: str
    target_name: str
    content_ko: str = Field(..., min_length=5)


class GuideResponse(BaseModel):
    id: str
    site_id: str
    target_type: str
    target_id: str
    target_name: str
    content_ko: str
    translations: dict[str, str]  # {lang: content}
    model_config = {"from_attributes": True}


# ── 관리자: 안전수칙 CRUD ──

@router.post("", response_model=GuideResponse, status_code=201)
def create_guide(
    req: GuideCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == req.site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404, detail="사업장을 찾을 수 없습니다")

    guide = SafetyGuide(
        site_id=req.site_id,
        target_type=req.target_type,
        target_id=req.target_id,
        target_name=req.target_name,
        content_ko=req.content_ko,
    )
    db.add(guide)
    db.commit()
    db.refresh(guide)

    return GuideResponse(
        id=guide.id, site_id=guide.site_id,
        target_type=guide.target_type, target_id=guide.target_id,
        target_name=guide.target_name, content_ko=guide.content_ko,
        translations={},
    )


@router.get("/list")
def list_guides(
    site_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site or site.company_id != user.company_id:
        raise HTTPException(status_code=404)

    guides = (
        db.query(SafetyGuide)
        .options(joinedload(SafetyGuide.translations))
        .filter(SafetyGuide.site_id == site_id)
        .all()
    )

    return [
        {
            "id": g.id, "target_type": g.target_type, "target_name": g.target_name,
            "content_ko": g.content_ko[:100],
            "languages": [t.language for t in g.translations],
        }
        for g in guides
    ]


# ── 번역 (GPT) ──

@router.post("/{guide_id}/translate")
def translate_guide(
    guide_id: str,
    lang: str = Query(..., description="vi, en, km, ne, my"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if lang not in SUPPORTED_LANGS or lang == "ko":
        raise HTTPException(status_code=400, detail=f"지원 언어: {', '.join(k for k in SUPPORTED_LANGS if k != 'ko')}")

    guide = db.query(SafetyGuide).filter(SafetyGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404)
    # cross-tenant 차단: 가이드의 사업장이 호출자 회사 소속인지 검증 (유료 GPT 호출 + content_ko 노출 방지)
    site = db.query(Site).filter(
        Site.id == guide.site_id, Site.company_id == user.company_id
    ).first()
    if not site:
        raise HTTPException(status_code=404)

    # 이미 번역 있으면 반환
    existing = db.query(SafetyGuideTranslation).filter(
        SafetyGuideTranslation.guide_id == guide_id,
        SafetyGuideTranslation.language == lang,
    ).first()
    if existing:
        return {"language": lang, "content": existing.content, "cached": True}

    # GPT 번역
    from app.main import law_agent  # 아무 agent나 사용 (같은 OpenAI client)
    if not law_agent.is_ready:
        raise HTTPException(status_code=503, detail="AI가 초기화되지 않았습니다")

    lang_name = SUPPORTED_LANGS[lang]
    translated = law_agent._chat(
        f"다음 한국어 산업안전 수칙을 {lang_name}로 번역하라. 산업 용어는 현지 작업자가 이해할 수 있게 쉽게 번역하라.\n\n{guide.content_ko}",
        system_override=f"당신은 한국어→{lang_name} 산업안전 전문 번역가다. 정확하고 쉬운 번역만 반환하라."
    )

    trans = SafetyGuideTranslation(guide_id=guide_id, language=lang, content=translated)
    db.add(trans)
    db.commit()

    return {"language": lang, "content": translated, "cached": False}


# ── QR 코드 (인증 불필요) ──

@router.get("/qr/{guide_id}")
def get_qr(guide_id: str, base_url: str = Query("http://localhost:3000")):
    """QR 코드 이미지 생성 — 스캔하면 안전수칙 페이지로 이동"""
    url = f"{base_url}/safety/{guide_id}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ── 공개 뷰 (인증 불필요 — QR 스캔용) ──

@router.get("/{guide_id}")
def get_guide_public(
    guide_id: str,
    lang: str = Query("ko"),
    db: Session = Depends(get_db),
):
    """안전수칙 조회 (QR 스캔 시 호출, 인증 불필요)"""
    guide = (
        db.query(SafetyGuide)
        .options(joinedload(SafetyGuide.translations))
        .filter(SafetyGuide.id == guide_id)
        .first()
    )
    if not guide:
        raise HTTPException(status_code=404, detail="안전수칙을 찾을 수 없습니다")

    content = guide.content_ko
    if lang != "ko":
        for t in guide.translations:
            if t.language == lang:
                content = t.content
                break

    return {
        "id": guide.id,
        "target_name": guide.target_name,
        "target_type": guide.target_type,
        "language": lang,
        "content": content,
        "available_languages": ["ko"] + [t.language for t in guide.translations],
    }


# ── 교육 이수 확인 (인증 불필요) ──

@router.post("/{guide_id}/ack")
def acknowledge_guide(
    guide_id: str,
    lang: str = Query("ko"),
    db: Session = Depends(get_db),
):
    """교육 이수 확인 기록"""
    guide = db.query(SafetyGuide).filter(SafetyGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404)

    record = TrainingRecord(guide_id=guide_id, language=lang)
    db.add(record)
    db.commit()

    return {"message": "교육 이수가 기록되었습니다", "guide_id": guide_id}
