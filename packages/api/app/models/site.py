import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    company: Mapped["Company"] = relationship(back_populates="sites")  # noqa: F821
    departments: Mapped[list["Department"]] = relationship(back_populates="site")  # noqa: F821
    processes: Mapped[list["Process"]] = relationship(back_populates="site")  # noqa: F821
    equipment_list: Mapped[list["Equipment"]] = relationship(back_populates="site")  # noqa: F821
    work_zones: Mapped[list["WorkZone"]] = relationship(back_populates="site")  # noqa: F821
