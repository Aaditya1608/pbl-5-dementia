from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.game_progress import GameProgress
from app.models.patients import Patient
from app.models.user import User, UserRole
from app.schemas.progress import GameProgressRequest,GameType,GameProgressResponse


def post_game_details(db: Session, payload:GameProgressRequest, current_user: User):
    if not current_user.role == UserRole.PATIENT :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user is not a patient!"
        )

    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user not found!"
        )

    if payload.mistakes > payload.attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The mistaked cannot be more than the attempts itself!"
            )
    

    try:
        new_progress = GameProgress(
            patient_id = patient.id,
            game_id = payload.game_id,
            score = payload.score,
            accuracy = payload.accuracy,
            attempts = payload.attempts,
            mistakes = payload.mistakes,
            duration_seconds = payload.duration_seconds,
            completed_at = payload.completed_at
        )

        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)

        return GameProgressResponse.model_validate(new_progress)

    except Exception:
        db.rollback()
        raise

def get_game_details(db: Session, current_user: User, game_id: GameType| None = None):
    if not current_user.role == UserRole.PATIENT :
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user is not a patient!"
            )
    
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user not found!"
        )

    q = db.query(GameProgress).filter(
         GameProgress.patient_id == patient.id
    )

    if game_id:
         q = q.filter(
              GameProgress.game_id == game_id
         )
    game_progresses = q.all()

    responses = []

    for progress in game_progresses:
         responses.append(
              GameProgressResponse.model_validate(progress)
         )
    return responses

def get_game_detail_session(db: Session, current_user: User, session_id: UUID):
    if not current_user.role == UserRole.PATIENT :
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user is not a patient!"
            )
    
    patient = db.query(Patient).filter(
        Patient.user_id == current_user.id
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user not found!"
        )

    q = db.query(GameProgress).filter(
         GameProgress.patient_id == patient.id,
         GameProgress.id == session_id
    ).first()

    return GameProgressResponse.model_validate(q)