"""
Sentinel SOS - Authentication Schemas.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: str = Field(..., min_length=7, max_length=32)
    password: str = Field(..., min_length=8)
    role: str = Field(default="citizen")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    role: str
    user_id: str


class UserContext(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    role: str
