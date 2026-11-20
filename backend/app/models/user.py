import uuid
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.patients import Patient
    from app.models.caregivers import Caregiver

from sqlalchemy import String, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    PATIENT="PATIENT"
    CAREGIVER="CAREGIVER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole,name="user_role"),
        nullable=False
    )
    patient: Mapped["Patient | None"] = relationship(
        "Patient",
        back_populates="user",
        uselist=False
    )

    caregiver: Mapped["Caregiver | None"] = relationship(
        "Caregiver",
        back_populates="user",
        uselist=False
    )


