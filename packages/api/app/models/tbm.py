"""TBM (Tool Box Meeting) 디지털화 모델"""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TBMSession(Base):
    __tablename__ = "tbm_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id: Mapped[str] = mapped_column(String(36), ForeignKey("sites.id"), nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    process_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # AI 생성 안건
    agenda: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    weather_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    attendees: Mapped[list["TBMAttendee"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class TBMAttendee(Base):
    __tablename__ = "tbm_attendees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("tbm_sessions.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["TBMSession"] = relationship(back_populates="attendees")
