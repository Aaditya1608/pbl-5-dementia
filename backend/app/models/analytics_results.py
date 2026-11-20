
import uuid

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.patients import Patient


class AnalyticsResult(Base):
    __tablename__ = "analytics_results"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False
    )

    game_id: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    cognitive_domain: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    trend: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False
    )

    # Analysis Period
    period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Generation Timestamp
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ORM Relationship
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="analytics_results"
    )

    # Database Constraints
    __table_args__ = (
        CheckConstraint(
            "game_id IS NULL OR game_id IN "
            "('GAME_001', 'GAME_002', 'GAME_003')",
            name="ck_analytics_results_game_id"
        ),
        CheckConstraint(
            "period_end >= period_start",
            name="ck_analytics_results_period"
        ),
        Index(
            "ix_analytics_patient_generated",
            "patient_id",
            "generated_at"
        ),
        Index(
            "ix_analytics_patient_game_generated",
            "patient_id",
            "game_id",
            "generated_at"
        )
    )
