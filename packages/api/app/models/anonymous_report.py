"""익명 위험 제보 모델 — 신원 정보 일절 저장 안 함"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnonymousReport(Base):
    __tablename__ = "anonymous_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    # 익명 토큰 — 제보자가 결과 확인할 때 사용 (사용자 식별 불가)
    anonymous_token: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    location_hint: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AI 분류
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="warning"
    )  # critical, warning, improvement
    ai_category: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # 관리자 조치
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="received"
    )  # received, reviewing, resolved
    admin_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # 주의: user_id, ip_address 등 신원 관련 컬럼 없음
