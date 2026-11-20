
from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.patients import Patient
from app.models.caregivers import Caregiver
from app.models.game_progress import GameProgress
from app.models.analytics_results import AnalyticsResult

from app.schemas.analytics import (
    AnalyticsOverviewResponse,
    GameCount,
    AnalyticsTrendsResponse,
    TrendDataPoint,
    GameAnalyticsResponse,
    GameAnalyticsItem,
    AnalyticsReportsResponse,
    AnalyticsReportItem
)


def get_authorized_patient(
    db: Session,
    current_user: User,
    patient_id: UUID
):
    caregiver = db.query(Caregiver).filter(
        Caregiver.user_id == current_user.id
    ).first()

    if not caregiver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caregiver profile not found!"
        )

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.caregiver_id == caregiver.id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not linked to this caregiver!"
        )

    return patient


def get_patient_overview(
    db: Session,
    current_user: User,
    patient_id: UUID
):
    patient = get_authorized_patient(
        db, current_user, patient_id
    )

    stats = db.query(
        func.count(GameProgress.id).label("total"),
        func.avg(GameProgress.score).label("avg_score"),
        func.avg(GameProgress.accuracy).label("avg_accuracy"),
        func.avg(GameProgress.duration_seconds).label("avg_duration"),
        func.max(GameProgress.completed_at).label("last_completed")
    ).filter(
        GameProgress.patient_id == patient.id
    ).one()

    breakdown = db.query(
        GameProgress.game_id,
        func.count(GameProgress.id).label("total_sessions")
    ).filter(
        GameProgress.patient_id == patient.id
    ).group_by(
        GameProgress.game_id
    ).all()

    return AnalyticsOverviewResponse(
        patient_id=patient.id,
        total_games_played=stats.total or 0,
        average_score=round(float(stats.avg_score or 0), 2),
        average_accuracy=round(float(stats.avg_accuracy or 0), 2),
        average_duration=round(float(stats.avg_duration or 0), 2),
        last_game_completed=stats.last_completed,
        games_breakdown=[
            GameCount(
                game_id=row.game_id.value,
                total_sessions=row.total_sessions
            )
            for row in breakdown
        ]
    )


def get_patient_trends(
    db: Session,
    current_user: User,
    patient_id: UUID,
    interval: str = "day",
    from_date: date | None = None,
    to_date: date | None = None
):
    patient = get_authorized_patient(
        db, current_user, patient_id
    )

    # interval is restricted to "day" or "week"
    query = db.query(
        func.date_trunc(
            interval, GameProgress.completed_at
        ).label("period"),
        func.count(GameProgress.id).label("total_sessions"),
        func.avg(GameProgress.score).label("avg_score"),
        func.avg(GameProgress.accuracy).label("avg_accuracy"),
        func.avg(GameProgress.duration_seconds).label("avg_duration"),
        func.sum(GameProgress.mistakes).label("total_mistakes")
    ).filter(
        GameProgress.patient_id == patient.id
    )

    if from_date:
        query = query.filter(
            GameProgress.completed_at >= from_date
        )

    if to_date:
        query = query.filter(
            GameProgress.completed_at < (
                datetime.combine(to_date, datetime.min.time())
                .replace(hour=0, minute=0)
                + __import__("datetime").timedelta(days=1)
            )
        )

    results = query.group_by(
        "period"
    ).order_by(
        "period"
    ).all()

    return AnalyticsTrendsResponse(
        patient_id=patient.id,
        interval=interval,
        trends=[
            TrendDataPoint(
                period=row.period,
                total_sessions=row.total_sessions,
                average_score=round(float(row.avg_score or 0), 2),
                average_accuracy=round(float(row.avg_accuracy or 0), 2),
                average_duration=round(float(row.avg_duration or 0), 2),
                total_mistakes=row.total_mistakes or 0
            )
            for row in results
        ]
    )


def get_game_wise_analytics(
    db: Session,
    current_user: User,
    patient_id: UUID
):
    patient = get_authorized_patient(
        db, current_user, patient_id
    )

    results = db.query(
        GameProgress.game_id,
        func.count(GameProgress.id).label("total_sessions"),
        func.avg(GameProgress.score).label("avg_score"),
        func.avg(GameProgress.accuracy).label("avg_accuracy"),
        func.avg(GameProgress.duration_seconds).label("avg_duration"),
        func.sum(GameProgress.attempts).label("total_attempts"),
        func.sum(GameProgress.mistakes).label("total_mistakes")
    ).filter(
        GameProgress.patient_id == patient.id
    ).group_by(
        GameProgress.game_id
    ).all()

    return GameAnalyticsResponse(
        patient_id=patient.id,
        games=[
            GameAnalyticsItem(
                game_id=row.game_id.value,
                total_sessions=row.total_sessions,
                average_score=round(float(row.avg_score or 0), 2),
                average_accuracy=round(float(row.avg_accuracy or 0), 2),
                average_duration=round(float(row.avg_duration or 0), 2),
                total_attempts=row.total_attempts or 0,
                total_mistakes=row.total_mistakes or 0
            )
            for row in results
        ]
    )


def get_patient_reports(
    db: Session,
    current_user: User,
    patient_id: UUID,
    from_date: date | None = None,
    to_date: date | None = None
):
    patient = get_authorized_patient(
        db, current_user, patient_id
    )

    query = db.query(AnalyticsResult).filter(
        AnalyticsResult.patient_id == patient.id
    )

    if from_date:
        query = query.filter(
            AnalyticsResult.period_start >= from_date
        )

    if to_date:
        query = query.filter(
            AnalyticsResult.period_end <= to_date
        )

    reports = query.order_by(
        AnalyticsResult.generated_at.desc()
    ).all()

    return AnalyticsReportsResponse(
        patient_id=patient.id,
        total_reports=len(reports),
        reports=[
            AnalyticsReportItem.model_validate(report)
            for report in reports
        ]
    )
