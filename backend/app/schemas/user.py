from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(...,min_length=8,max_length=128)
    full_name: str = Field(min_length=2,max_length=150)
    dob: date

class PatientResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user_id: str
    patient_id: str
    email: EmailStr
    full_name: str
    dob: date
    role: str

    model_config = ConfigDict(from_attributes=True)

class CaregiverRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(...,min_length=8,max_length=128)
    full_name: str = Field(min_length=2,max_length=150)
    phone_number: str

class CaregiverResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user_id: str
    caregiver_id: str
    email: EmailStr
    full_name: str
    phone_number: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserLoginRequest(BaseModel):
    model_config= ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8,max_length=128)

class UserLoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user_id: str
    role: str
    profile_id: str
    full_name: str

class UserDetails(BaseModel):
    message: str
    user_id: str
    role: str