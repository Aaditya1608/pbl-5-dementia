import uuid
import enum
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.caregivers import Caregiver
    from app.models.patients import Patient
from datetime import datetime
from sqlalchemy import ForeignKey, Enum,func,DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class CaregiverRequestStatus(str,enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class CaregiverRequest(Base):
    __tablename__="caregiver_requests"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    caregiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("caregivers.id"),
        nullable=False
    )

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id"),
        nullable=False
    )

    status: Mapped[CaregiverRequestStatus] = mapped_column(
        Enum(
            CaregiverRequestStatus,
            name="caregiver_request_status"
        ),
        nullable=False,
        default=CaregiverRequestStatus.PENDING
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    caregiver: Mapped["Caregiver"] = relationship(
        "Caregiver",
        back_populates="caregiver_requests"
    )

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="caregiver_requests"
    )