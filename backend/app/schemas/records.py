from datetime import date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class PatientRecord(BaseModel):
    model_config=ConfigDict(extra="forbid",from_attributes=True)
    id: UUID
    full_name: str= Field(min_length=2,max_length=150)
    dob: date
    email: EmailStr



