"""
Sentinel SOS - Authentication Service.

Handles user registration, authentication verification, and JWT generation.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import SentinelException, UnauthorizedException
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.sql.role import Role
from app.models.sql.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, req: RegisterRequest) -> User:
        if self.user_repo.get_by_email(req.email):
            raise SentinelException("An account with this email address already exists.", code="USER_EXISTS")

        if self.user_repo.get_by_phone(req.phone_number):
            raise SentinelException("An account with this phone number already exists.", code="PHONE_EXISTS")

        # Resolve or create role
        role = self.db.query(Role).filter(Role.name == req.role.lower()).first()
        if not role:
            role = Role(name=req.role.lower(), description=f"Default {req.role} role")
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)

        new_user = User(
            email=req.email.lower(),
            full_name=req.full_name,
            phone_number=req.phone_number,
            hashed_password=get_password_hash(req.password),
            role_id=role.id,
            is_active=True,
        )
        return self.user_repo.create(new_user)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Please contact system administration.")

        role_name = user.role.name if user.role else "citizen"
        access_token = create_access_token(
            subject=user.id,
            role=role_name,
            extra_claims={"email": user.email, "name": user.full_name},
        )

        return TokenResponse(
            access_token=access_token,
            role=role_name,
            user_id=user.id,
            expires_in_minutes=60,
        )
