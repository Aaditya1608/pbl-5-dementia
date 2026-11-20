import uuid
from datetime import datetime, date
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.caregivers import Caregiver
    from app.models.caregiver_requests import CaregiverRequest
    from app.models.game_progress import GameProgress
    from app.models.analytics_results import AnalyticsResult

class Patient(Base):
    __tablename__="patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id",ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    caregiver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("caregivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Patient Information
    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    dob: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="patient"
    )

    caregiver: Mapped["Caregiver | None"] = relationship(
        "Caregiver",
        back_populates="patients"
    )

    caregiver_requests: Mapped[list["CaregiverRequest"]] = relationship(
        "CaregiverRequest",
        back_populates="patient"
    )

    game_progress: Mapped[list["GameProgress"]] = relationship(
        "GameProgress",
        back_populates="patient"
    )
    analytics_results: Mapped[list["AnalyticsResult"]] = relationship(
        "AnalyticsResult",
        back_populates="patient"
    )