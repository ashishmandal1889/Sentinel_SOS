"""
Sentinel SOS - Users Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.db.sql import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserRepository(db).get_by_id(current_user.user_id)
    return user


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    payload: UserUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = UserRepository(db)
    user = repo.get_by_id(current_user.user_id)
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number
    db.commit()
    db.refresh(user)
    return user
