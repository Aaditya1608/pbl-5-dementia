from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.dependencies.auth import get_current_user, require_role,security
from app.models.game_progress import GameType
from app.models.user import User
from app.schemas.progress import GameProgressRequest, GameProgressResponse
from app.services.progress import get_game_detail_session, post_game_details, get_game_details

router = APIRouter(prefix='/game-progress',tags=["Game Progress"])

@router.post(
    "/",
    response_model=GameProgressResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_progress(payload: GameProgressRequest,db: Session = Depends(get_db), current_user: User = Depends(require_role("PATIENT"))):
    return post_game_details(db=db,payload=payload,current_user=current_user)

@router.get(
    "/",
    response_model=list[GameProgressResponse],
    status_code=status.HTTP_200_OK
)
def get_all_progresses(game_id:GameType | None = None ,db: Session = Depends(get_db), current_user: User = Depends(require_role("PATIENT"))):
    return get_game_details(db=db,current_user=current_user,game_id=game_id)

@router.get(
    "/{session_id}",
    response_model=GameProgressResponse,
    status_code=status.HTTP_200_OK
)
def get_progress(session_id: UUID ,db: Session = Depends(get_db), current_user: User = Depends(require_role("PATIENT"))):
    return get_game_detail_session(db=db,current_user=current_user,session_id=session_id)