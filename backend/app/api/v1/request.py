from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_role,security
from app.models.user import User
from app.schemas.request import CaregiverRequestCancel, CaregiverRequestUpdate, CaregiverResponse, CaregiverSendRequest, PatientResponses, ToPatient
from app.services.request import caregiver_request, get_caregivers_requests,get_patients_requests, update_caregiver_request, cancel_caregiver_request
from app.schemas.records import PatientRecord
from app.services.patient_records import get_patient_records 

router = APIRouter(prefix='/caregiver-requests',tags=["Caregiver Request"])

@router.post(
    "/",
    response_model=CaregiverResponse,
    status_code=status.HTTP_201_CREATED
)
def create_request(
    payload : CaregiverSendRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return caregiver_request(db=db,payload=payload,current_user=current_user)

@router.get(
    "/incoming",
    response_model=list[PatientResponses],
    status_code=status.HTTP_200_OK
)
def get_incoming_requests(
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role("PATIENT"))
):
    return get_patients_requests(db=db,current_user=current_user)

@router.patch(
    "/{request_id}",
    status_code=status.HTTP_200_OK
)
def respond_to_request(
    request_id: UUID,
    payload: CaregiverRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("PATIENT"))
):
    return update_caregiver_request(db=db,current_user=current_user,request_id=request_id,payload=payload)

@router.get(
    "/sent",
    response_model=list[ToPatient],
    status_code=status.HTTP_200_OK
)
def get_outgoing_requests(
        db: Session = Depends(get_db),
        current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_caregivers_requests(db=db,current_user=current_user)

@router.patch(
    "/cancel/{request_id}",
    status_code=status.HTTP_200_OK
)
def cancel_request(
    request_id: UUID,
    payload: CaregiverRequestCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return cancel_caregiver_request(db=db,current_user=current_user,request_id=request_id,payload=payload)

@router.get(
    "/patients",
    response_model=list[PatientRecord],
    status_code=status.HTTP_200_OK
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_patient_records(db=db, current_user=current_user)