from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.security import create_access_token, hash_password
from app.models.revoked_tokens import RevokedTokens
from app.models.user import User, UserRole
from app.models.patients import Patient
from app.models.caregivers import Caregiver
from app.schemas.user import ( PatientRegisterRequest, PatientResponse, CaregiverRegisterRequest, CaregiverResponse, UserLoginRequest, UserLoginResponse )
from app.core.security import password_hasher
def register_patient(payload: PatientRegisterRequest,db: Session):
    existing_email = db.query(User).filter(User.email == payload.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered!"
        )
    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.PATIENT
    )
    try:
        db.add(new_user)
        db.flush()

        new_patient = Patient(
            user_id=new_user.id,
            full_name = payload.full_name,
            dob = payload.dob
        )

        db.add(new_patient)
        db.commit()

        db.refresh(new_user)
        db.refresh(new_patient)

        access_token = create_access_token(
            user_id=str(new_user.id),
            role=new_user.role.value
        )

        return PatientResponse(
            message="Patient registered successfully",
            access_token=access_token,
            token_type="bearer",
            user_id=str(new_user.id),
            patient_id=str(new_patient.id),
            email=new_user.email,
            full_name=new_patient.full_name,
            dob=new_patient.dob,
            role=new_user.role.value
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration could not be completed. Email may already be registered."
        )
    except Exception:
        db.rollback()
        raise

def register_caregiver(payload: CaregiverRegisterRequest,db: Session):
    existing_email = db.query(User).filter(User.email == payload.email).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered!"
        )
    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.CAREGIVER
    )
    try:
        db.add(new_user)
        db.flush()

        new_caregiver = Caregiver(
            user_id=new_user.id,
            full_name = payload.full_name,
            phone_number = payload.phone_number
        )

        db.add(new_caregiver)
        db.commit()

        db.refresh(new_user)
        db.refresh(new_caregiver)

        access_token = create_access_token(
            user_id=str(new_user.id),
            role=new_user.role.value
        )

        return CaregiverResponse(
            message="Caregiver registered successfully",
            access_token=access_token,
            token_type="bearer",
            user_id=str(new_user.id),
            caregiver_id=str(new_caregiver.id),
            email=new_user.email,
            full_name=new_caregiver.full_name,
            phone_number=new_caregiver.phone_number,
            role=new_user.role.value
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration could not be completed. Email may already be registered."
        )
    except Exception:
        db.rollback()
        raise


def login(payload: UserLoginRequest, db: Session):

    existing_email = db.query(User).filter(
        User.email == payload.email
    ).first()

    if not existing_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not password_hasher.verify(
        payload.password,
        existing_email.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


    if existing_email.role == UserRole.PATIENT:

        profile = db.query(Patient).filter(
            Patient.user_id == existing_email.id
        ).first()

    elif existing_email.role == UserRole.CAREGIVER:

        profile = db.query(Caregiver).filter(
            Caregiver.user_id == existing_email.id
        ).first()

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid user role"
        )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User profile is missing"
        )

    # Generate JWT

    access_token = create_access_token(
        user_id=str(existing_email.id),
        role=existing_email.role.value
    )


    return UserLoginResponse(
        message="User logged in successfully",
        access_token=access_token,
        token_type="bearer",
        user_id=str(existing_email.id),
        role=existing_email.role.value,
        profile_id=str(profile.id),
        full_name=profile.full_name
    )

def revoke_token(db: Session, payload: dict):
    revoked_token = RevokedTokens(
        token_jti=payload["jti"],
        expires_at=datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        )
    )

    db.add(revoked_token)
    db.commit()

    