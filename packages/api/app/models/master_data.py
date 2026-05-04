import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped["Site"] = relationship(back_populates="departments")  # noqa: F821


class Process(Base):
    __tablename__ = "processes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped["Site"] = relationship(back_populates="processes")  # noqa: F821
    equipment_list: Mapped[list["Equipment"]] = relationship(back_populates="process")


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    process_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("processes.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped["Site"] = relationship(back_populates="equipment_list")  # noqa: F821
    process: Mapped["Process | None"] = relationship(back_populates="equipment_list")


class WorkZone(Base):
    __tablename__ = "work_zones"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    site_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sites.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped["Site"] = relationship(back_populates="work_zones")  # noqa: F821
