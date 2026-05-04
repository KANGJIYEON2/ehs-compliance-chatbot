"""다국어 안전 안내 모델"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SafetyGuide(Base):
    __tablename__ = "safety_guides"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)  # equipment, work_zone
    target_id: Mapped[str] = mapped_column(String(36), nullable=False)
    target_name: Mapped[str] = mapped_column(String(200), nullable=False)
    content_ko: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    translations: Mapped[list["SafetyGuideTranslation"]] = relationship(
        back_populates="guide", cascade="all, delete-orphan"
    )


class SafetyGuideTranslation(Base):
    __tablename__ = "safety_guide_translations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    guide_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("safety_guides.id"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False)  # vi, km, ne, my, en
    content: Mapped[str] = mapped_column(Text, nullable=False)
    translated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    guide: Mapped["SafetyGuide"] = relationship(back_populates="translations")


class TrainingRecord(Base):
    __tablename__ = "training_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    guide_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("safety_guides.id"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
