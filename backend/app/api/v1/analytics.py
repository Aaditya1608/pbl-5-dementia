
from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_role
from app.models.user import User
from app.models.game_progress import GameType

from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    AnalyticsTrendsResponse,
    GameAnalyticsResponse,
    AnalyticsReportsResponse
)

from app.services.analytics import (
    get_patient_overview,
    get_patient_trends,
    get_game_wise_analytics,
    get_patient_reports
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# 1. Patient overview

@router.get(
    "/patients/{patient_id}/overview",
    response_model=AnalyticsOverviewResponse,
    status_code=status.HTTP_200_OK
)
def patient_overview(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_patient_overview(
        db=db,
        current_user=current_user,
        patient_id=patient_id
    )


# 2. Patient performance trends

@router.get(
    "/patients/{patient_id}/trends",
    response_model=AnalyticsTrendsResponse,
    status_code=status.HTTP_200_OK
)
def patient_trends(
    patient_id: UUID,
    interval: Literal["day", "week"] = Query(default="day"),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_patient_trends(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        interval=interval,
        from_date=from_date,
        to_date=to_date
    )


# 3. Game-wise analytics

@router.get(
    "/patients/{patient_id}/games",
    response_model=GameAnalyticsResponse,
    status_code=status.HTTP_200_OK
)
def game_wise_analytics(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_game_wise_analytics(
        db=db,
        current_user=current_user,
        patient_id=patient_id
    )


# 4. Historical analytics reports

@router.get(
    "/patients/{patient_id}/reports",
    response_model=AnalyticsReportsResponse,
    status_code=status.HTTP_200_OK
)
def patient_reports(
    patient_id: UUID,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("CAREGIVER"))
):
    return get_patient_reports(
        db=db,
        current_user=current_user,
        patient_id=patient_id,
        from_date=from_date,
        to_date=to_date
    )
