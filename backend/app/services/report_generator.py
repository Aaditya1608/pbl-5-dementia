
import logging

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from sqlalchemy.orm import Session

from app.models.patients import Patient
from app.models.game_progress import GameProgress
from app.models.analytics_results import AnalyticsResult


logger = logging.getLogger(__name__)

INDIA_TZ = ZoneInfo("Asia/Kolkata")


def generate_daily_reports(
    db: Session,
    report_date: date | None = None
):
    if report_date is None:
        report_date = (
            datetime.now(INDIA_TZ).date() - timedelta(days=1)
        )

    start_time = datetime.combine(
        report_date, time.min, tzinfo=INDIA_TZ
    )

    end_time = start_time + timedelta(days=1)

    patients = db.query(Patient).all()

    reports_created = 0

    for patient in patients:
        try:
            sessions = db.query(GameProgress).filter(
                GameProgress.patient_id == patient.id,
                GameProgress.completed_at >= start_time,
                GameProgress.completed_at < end_time
            ).all()

            records = [
                {
                    "game_id": (
                        session.game_id.value
                        if hasattr(session.game_id, "value")
                        else str(session.game_id)
                    ),
                    "score": session.score,
                    "accuracy": session.accuracy,
                    "attempts": session.attempts,
                    "mistakes": session.mistakes,
                    "duration_seconds": session.duration_seconds
                }
                for session in sessions
            ]

            df = pd.DataFrame(records)

            # Default values for a day with no sessions.
            total_sessions = len(df)
            average_accuracy = 0.0
            average_duration = 0.0
            total_attempts = 0
            total_mistakes = 0
            game_breakdown = []
            observation = (
                "No game session records were available "
                "for this reporting period."
            )

            if not df.empty:
                average_accuracy = round(
                    float(df["accuracy"].mean()), 2
                )

                average_duration = round(
                    float(df["duration_seconds"].mean()), 2
                )

                total_attempts = int(df["attempts"].sum())
                total_mistakes = int(df["mistakes"].sum())

                grouped = df.groupby("game_id")

                for game_id, group in grouped:
                    game_breakdown.append({
                        "game_id": str(game_id),
                        "total_sessions": int(len(group)),
                        "average_score": round(
                            float(group["score"].mean()), 2
                        ),
                        "average_accuracy": round(
                            float(group["accuracy"].mean()), 2
                        ),
                        "average_duration": round(
                            float(group["duration_seconds"].mean()), 2
                        )
                    })

                observation = (
                    f"{total_sessions} game sessions were recorded "
                    f"during this reporting period. "
                    f"Average recorded accuracy was "
                    f"{average_accuracy}%."
                )

            summary = {
                "total_sessions": total_sessions,
                "average_accuracy": average_accuracy,
                "average_duration": average_duration,
                "total_attempts": total_attempts,
                "total_mistakes": total_mistakes,
                "game_breakdown": game_breakdown,
                "observation": observation
            }

            trend = "INSUFFICIENT_DATA"

            existing_report = db.query(AnalyticsResult).filter(
                AnalyticsResult.patient_id == patient.id,
                AnalyticsResult.game_id.is_(None),
                AnalyticsResult.cognitive_domain
                    == "OVERALL_GAME_PERFORMANCE",
                AnalyticsResult.period_start == report_date,
                AnalyticsResult.period_end == report_date
            ).first()

            if existing_report:
                existing_report.trend = trend
                existing_report.summary = summary
                existing_report.generated_at = datetime.now(
                    timezone.utc
                )
            else:
                new_report = AnalyticsResult(
                    patient_id=patient.id,
                    game_id=None,
                    cognitive_domain="OVERALL_GAME_PERFORMANCE",
                    trend=trend,
                    summary=summary,
                    period_start=report_date,
                    period_end=report_date
                )

                db.add(new_report)

            db.commit()
            reports_created += 1

        except Exception:
            db.rollback()

            logger.exception(
                "Failed to generate report for patient %s",
                patient.id
            )

    logger.info(
        "Daily analytics job completed. Reports processed: %s",
        reports_created
    )

    return reports_created
