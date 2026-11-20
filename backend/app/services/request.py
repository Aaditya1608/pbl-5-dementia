from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.caregiver_requests import CaregiverRequest, CaregiverRequestStatus
from app.models.caregivers import Caregiver
from app.models.patients import Patient
from app.models.user import User, UserRole
from app.schemas.request import CaregiverRequestAction, CaregiverRequestCancel, CaregiverRequestUpdate, CaregiverSendRequest, CaregiverResponse, PatientResponses, RequestCancel, ToPatient

def caregiver_request(
    db: Session,
    payload: CaregiverSendRequest,
    current_user: User
):

    patient = db.query(User).filter(
        User.email == payload.email
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="User not registered"
        )

    if patient.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=403,
            detail="User is not a patient"
        )

    caregiver = db.query(Caregiver).filter(
        Caregiver.user_id == current_user.id
    ).first()

    if not caregiver:
        raise HTTPException(
            status_code=404,
            detail="Caregiver profile not found"
        )
    patient_profile = db.query(Patient).filter(
        Patient.user_id == patient.id
    ).first()

    if not patient_profile:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
    )
    
    new_request = CaregiverRequest(
        patient_id=patient_profile.id,
        caregiver_id=caregiver.id,
        status=CaregiverRequestStatus.PENDING
    )

    try:
        existing_request = db.query(CaregiverRequest).filter(
            CaregiverRequest.patient_id == patient_profile.id,
            CaregiverRequest.caregiver_id == caregiver.id
        ).first()

        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The request to this patient already exists!"
            )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return CaregiverResponse(
            id=new_request.id,
            patient_email=patient.email,
            status=new_request.status
        )

    except Exception:
        db.rollback()
        raise

def get_patients_requests(db: Session, current_user: User):
    if current_user.role != UserRole.PATIENT:
            raise HTTPException(
                status_code=403,
                detail="User is not a patient"
    )
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    requests = db.query(CaregiverRequest).filter(
        CaregiverRequest.patient_id == patient.id,
        CaregiverRequest.status!=CaregiverRequestStatus.CANCELLED
    ).all()

    responses = []

    for request in requests:
        caregiver = db.query(Caregiver).filter(
            Caregiver.id == request.caregiver_id
        ).first()

        caregiver_user = db.query(User).filter(
            User.id == caregiver.user_id
        ).first()

        responses.append(
            PatientResponses(
                caregiver_id=caregiver.id,
                caregiver_name=caregiver.full_name,
                caregiver_email=caregiver_user.email,
                status= request.status
            )
        )
    return responses
    
def update_caregiver_request(db: Session, current_user: User, request_id: UUID, payload: CaregiverRequestUpdate):
    if current_user.role!= UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not a patient"
        )
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    try:
        request = db.query(CaregiverRequest).filter(
            CaregiverRequest.id == request_id,
            CaregiverRequest.patient_id == patient.id
        ).with_for_update().first()

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caregiver request not found"
            )
        if request.status != CaregiverRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been processed"
            )

        if payload.action == CaregiverRequestAction.ACCEPT:
            if patient.caregiver_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Patient already has an active caregiver"
                )

            request.status = CaregiverRequestStatus.ACCEPTED
            patient.caregiver_id = request.caregiver_id

        elif payload.action == CaregiverRequestAction.REJECT:
            request.status = CaregiverRequestStatus.REJECTED

        request.responded_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(request)

        messages = {
            CaregiverRequestAction.ACCEPT: "Caregiver request accepted successfully",
            CaregiverRequestAction.REJECT: "Caregiver request rejected successfully"
        }

        return{
            "message": messages[payload.action],
            "request_id": str(request_id),
            "status": request.status
        }
    except Exception:
        db.rollback()
        raise

def get_caregivers_requests(db: Session, current_user: User):
    if current_user.role != UserRole.CAREGIVER:
            raise HTTPException(
                status_code=403,
                detail="User is not a caregiver"
    )
    caregiver = db.query(Caregiver).filter(
        Caregiver.user_id == current_user.id
    ).first()

    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found"
        )
    requests = db.query(CaregiverRequest).filter(
        CaregiverRequest.caregiver_id == caregiver.id,
        CaregiverRequest.status!=CaregiverRequestStatus.CANCELLED
    ).all()

    responses = []

    for request in requests:
        patient = db.query(Patient).filter(
            Patient.id == request.patient_id
        ).first()

        patient_user = db.query(User).filter(
            User.id == patient.user_id
        ).first()

        responses.append(
            ToPatient(
                patient_id=patient.id,
                patient_name=patient.full_name,
                patient_email=patient_user.email,
                status= request.status
            )
        )
    return responses

def cancel_caregiver_request(db: Session, current_user: User, request_id: UUID, payload: CaregiverRequestCancel):
    if current_user.role!= UserRole.CAREGIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not a caregiver"
        )
    caregiver = db.query(Caregiver).filter(
        Caregiver.user_id == current_user.id
    ).first()

    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found"
        )

    try:
        request = db.query(CaregiverRequest).filter(
            CaregiverRequest.id == request_id,
            CaregiverRequest.caregiver_id == caregiver.id
        ).with_for_update().first()

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caregiver request not found"
            )
        if request.status != CaregiverRequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been processed"
            )

        request.status = CaregiverRequestStatus.CANCELLED
        request.responded_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(request)

        return{
            "message": "The request is cancelled succesfully",
            "request_id": str(request_id),
            "status": request.status
        }
    except Exception:
        db.rollback()
        raise


