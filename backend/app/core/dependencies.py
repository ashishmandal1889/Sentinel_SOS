"""
Sentinel SOS - Dependency Injection Providers.

Provides reusable FastAPI dependencies for authentication, role enforcement,
and database connections.
"""

from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status
from app.core.security import decode_access_token
from app.core.exceptions import ForbiddenException, UnauthorizedException


class AuthenticatedUser:
    """Represents a validated authenticated user identity and role."""
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_responder(self) -> bool:
        return self.role in ("responder", "admin")


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer <JWT_TOKEN>"),
) -> AuthenticatedUser:
    """
    Extracts and validates the current user identity from the Bearer token.
    Never trusts user IDs provided in the request body.
    """
    if not authorization:
        raise UnauthorizedException("Missing Authorization header.")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid Authorization format. Expected 'Bearer <token>'.")

    token = parts[1]
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    role = payload.get("role", "citizen")

    if not user_id:
        raise UnauthorizedException("Invalid token payload: missing subject identifier.")

    return AuthenticatedUser(user_id=str(user_id), role=str(role))


def require_roles(allowed_roles: List[str]):
    """Factory dependency that restricts endpoint access to specified roles."""
    async def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Access denied. User role '{current_user.role}' is not in allowed roles: {allowed_roles}"
            )
        return current_user
    return role_checker
