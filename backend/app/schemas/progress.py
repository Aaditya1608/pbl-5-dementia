from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.game_progress import GameType

class GameProgressRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    game_id: GameType
    score: int = Field(ge=0)
    accuracy: float = Field(ge=0, le=100)
    attempts: int = Field(ge=0)
    mistakes: int = Field(ge=0)
    duration_seconds: int = Field(gt=0)
    completed_at: datetime

class GameProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    game_id: GameType
    score: int
    accuracy: float
    attempts: int
    mistakes: int
    duration_seconds: int
    completed_at: datetime
    created_at: datetime