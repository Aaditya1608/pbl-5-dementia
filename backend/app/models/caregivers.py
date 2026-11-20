import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.patients import Patient
    from app.models.user import User
    from app.models.caregiver_requests import CaregiverRequest

class Caregiver(Base):
    __tablename__ = "caregivers"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign Key -> users.id
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    # Caregiver Information
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ORM Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="caregiver"
    )

    patients: Mapped[list["Patient"]] = relationship(
        "Patient",
        back_populates="caregiver"
    )

    caregiver_requests: Mapped[list["CaregiverRequest"]] = relationship(
        "CaregiverRequest",
        back_populates="caregiver"
    )
