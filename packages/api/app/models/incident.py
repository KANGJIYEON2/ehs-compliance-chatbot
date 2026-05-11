import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IncidentType(str, enum.Enum):
    caught = "caught"           # 끼임
    fall = "fall"               # 추락
    collision = "collision"     # 충돌
    electric = "electric"       # 감전
    fire = "fire"               # 화재
    suffocation = "suffocation" # 질식
    falling_object = "falling_object"  # 낙하물
    chemical = "chemical"       # 화학물질
    other = "other"             # 기타


class Severity(str, enum.Enum):
    death = "death"             # 사망
    serious = "serious"         # 중상
    minor = "minor"             # 경상
    near_miss = "near_miss"     # 아차사고


class IncidentStatus(str, enum.Enum):
    reported = "reported"           # 접수
    investigating = "investigating" # 조치중
    resolved = "resolved"           # 조치완료
    monitoring = "monitoring"       # 재발관리


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    reporter_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )

    # 사고 정보
    incident_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 위치/관련 정보
    work_zone_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("work_zones.id"), nullable=True
    )
    process_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("processes.id"), nullable=True
    )
    equipment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("equipment.id"), nullable=True
    )
    department_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("departments.id"), nullable=True
    )

    # 상세
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cause_estimate: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 상태
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=IncidentStatus.reported.value
    )

    # 조치 담당자 + 기한
    assignee_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    assignee_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    site: Mapped["Site"] = relationship(foreign_keys=[site_id])  # noqa: F821
    reporter: Mapped["User"] = relationship(foreign_keys=[reporter_id])  # noqa: F821
    attachments: Mapped[list["IncidentAttachment"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan"
    )


class IncidentAttachment(Base):
    __tablename__ = "incident_attachments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    incident_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("incidents.id"), nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    incident: Mapped["Incident"] = relationship(back_populates="attachments")
