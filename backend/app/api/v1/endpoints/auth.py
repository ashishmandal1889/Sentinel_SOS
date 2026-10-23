"""
Sentinel SOS - Authentication Endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.db.sql import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserContext
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user (citizen or responder)."""
    auth_service = AuthService(db)
    user = auth_service.register(payload)
    return auth_service.login(payload.email, payload.password)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT token."""
    auth_service = AuthService(db)
    return auth_service.login(payload.email, payload.password)


@router.get("/me", response_model=UserContext)
def get_current_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves profile of currently authenticated user."""
    from app.repositories.user_repository import UserRepository
    user = UserRepository(db).get_by_id(current_user.user_id)
    return UserContext(
        user_id=current_user.user_id,
        email=user.email if user else "user@example.com",
        full_name=user.full_name if user else "Citizen",
        role=current_user.role,
    )
