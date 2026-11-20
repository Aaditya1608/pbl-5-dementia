from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.dependencies.auth import get_current_user,security
from app.schemas.user import PatientRegisterRequest, PatientResponse, CaregiverRegisterRequest, CaregiverResponse, UserLoginRequest, UserLoginResponse, UserDetails
from app.services.auth import register_patient, register_caregiver, login, revoke_token

router = APIRouter(prefix='/auth',tags=["Auth"])

@router.post(
    "/patient/register",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def patient_register(
    payload: PatientRegisterRequest,
    db: Session = Depends(get_db)
):
    return register_patient(db=db,payload=payload) 

@router.post(
    "/caregiver/register",
    response_model=CaregiverResponse,
    status_code=status.HTTP_201_CREATED
)
def caregiver_register(
    payload: CaregiverRegisterRequest,
    db: Session = Depends(get_db)
):
    return register_caregiver(db=db,payload=payload)

@router.post(
    "/login",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK
)
def authenticate_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    return login(payload=payload,db=db)

@router.get(
    "/me",
    response_model=UserDetails,
    status_code=status.HTTP_200_OK
)
def get_authenticated_user(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return UserDetails(
        message="User retrieved successfully",
        user_id=str(current_user.id),
        role=current_user.role.value
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)

    revoke_token(db,payload)

    return {
        "message": "Logged out successfully"
    }
    