import uuid
import enum

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.patients import Patient

class GameType(str, enum.Enum):
    GAME_001 = "GAME_001"
    GAME_002 = "GAME_002"
    GAME_003 = "GAME_003"

class GameProgress(Base):
    __tablename__="game_progress"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False
    )

    game_id: Mapped[GameType] = mapped_column(
        Enum(GameType, name="game_type"),
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    accuracy: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    mistakes: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Timestamps
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # ORM Relationship
    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="game_progress"
    )

    # Database Constraints
    __table_args__ = (
        CheckConstraint(
            "score >= 0",
            name="ck_game_progress_score_nonnegative"
        ),
        CheckConstraint(
            "accuracy >= 0 AND accuracy <= 100",
            name="ck_game_progress_accuracy_range"
        ),
        CheckConstraint(
            "attempts >= 0",
            name="ck_game_progress_attempts_nonnegative"
        ),
        CheckConstraint(
            "mistakes >= 0",
            name="ck_game_progress_mistakes_nonnegative"
        ),
        CheckConstraint(
            "duration_seconds >= 0",
            name="ck_game_progress_duration_nonnegative"
        ),
        Index(
            "ix_game_progress_patient_completed",
            "patient_id",
            "completed_at"
        )
    )


