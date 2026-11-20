from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GameCount(BaseModel):
    game_id: str
    total_sessions: int


class AnalyticsOverviewResponse(BaseModel):
    patient_id: UUID
    total_games_played: int
    average_score: float
    average_accuracy: float
    average_duration: float
    last_game_completed: datetime | None
    games_breakdown: list[GameCount]


class TrendDataPoint(BaseModel):
    period: datetime
    total_sessions: int
    average_score: float
    average_accuracy: float
    average_duration: float
    total_mistakes: int


class AnalyticsTrendsResponse(BaseModel):
    patient_id: UUID
    interval: str
    trends: list[TrendDataPoint]


class GameAnalyticsItem(BaseModel):
    game_id: str
    total_sessions: int
    average_score: float
    average_accuracy: float
    average_duration: float
    total_attempts: int
    total_mistakes: int


class GameAnalyticsResponse(BaseModel):
    patient_id: UUID
    games: list[GameAnalyticsItem]


class AnalyticsReportItem(BaseModel):
    id: UUID
    game_id: str | None
    cognitive_domain: str
    trend: str
    summary: dict
    period_start: date
    period_end: date
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyticsReportsResponse(BaseModel):
    patient_id: UUID
    total_reports: int
    reports: list[AnalyticsReportItem]
