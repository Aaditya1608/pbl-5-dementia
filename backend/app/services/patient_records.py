from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.caregivers import Caregiver
from app.models.patients import Patient
from app.models.user import User
from app.schemas.records import PatientRecord

def get_patient_records(db: Session, current_user: User) -> list[PatientRecord]:
    caregiver = db.query(Caregiver).filter(
        Caregiver.user_id == current_user.id
    ).first()

    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found!"
        )

    patients = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.caregiver_id == caregiver.id)
        .all()
    )

    return [
        PatientRecord(
            id=patient.id,
            full_name=patient.full_name,
            dob=patient.dob,
            email=patient.user.email
        )
        for patient in patients
    ]