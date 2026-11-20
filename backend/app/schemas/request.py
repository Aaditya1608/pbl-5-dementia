from datetime import date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CaregiverSendRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    email: EmailStr

class CaregiverResponse(BaseModel):
    id: UUID
    patient_email: EmailStr
    status: str

class PatientResponses(BaseModel):
    caregiver_id: UUID
    caregiver_name: str
    caregiver_email: EmailStr
    status: str

class CaregiverRequestAction(str,Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"

class CaregiverRequestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: CaregiverRequestAction

class ToPatient(BaseModel):
    patient_id: UUID
    patient_name: str
    patient_email: EmailStr
    status: str

class RequestCancel(str,Enum):
    CANCEL = "CANCEL"

class CaregiverRequestCancel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: RequestCancel