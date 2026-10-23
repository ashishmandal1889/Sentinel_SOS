"""
Sentinel SOS - Emergency Contact Schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    contact_name: str = Field(..., min_length=2, max_length=255)
    relationship_label: str = Field(..., min_length=2, max_length=64)
    phone_number: str = Field(..., min_length=7, max_length=32)
    email: Optional[EmailStr] = None
    priority_order: int = Field(default=1, ge=1, le=10)


class ContactUpdate(BaseModel):
    contact_name: Optional[str] = None
    relationship_label: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    priority_order: Optional[int] = None
    is_active: Optional[bool] = None


class ContactResponse(BaseModel):
    id: str
    user_id: str
    contact_name: str
    relationship_label: str
    phone_number: str
    email: Optional[str] = None
    priority_order: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
