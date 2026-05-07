"""위험성평가 자동화 모델"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id: Mapped[str] = mapped_column(String(36), ForeignKey("sites.id"), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # 작업 정보
    process_name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)

    # AI 분석 결과 (JSON)
    hazards: Mapped[str] = mapped_column(Text, nullable=False)  # 유해위험요인 JSON
    risk_matrix: Mapped[str] = mapped_column(Text, nullable=False)  # 위험도 매트릭스 JSON
    measures: Mapped[str] = mapped_column(Text, nullable=False)  # 감소대책 JSON
    legal_basis: Mapped[str | None] = mapped_column(Text, nullable=True)  # 법령근거 JSON

    # 평가 결과
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # high/medium/low
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft/reviewed/approved

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
