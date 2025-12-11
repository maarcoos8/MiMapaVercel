from pydantic import BaseModel, EmailStr
from datetime import datetime


class VisitCreate(BaseModel):
    """Schema para registrar una nueva visita"""
    visited_user_email: EmailStr


class VisitResponse(BaseModel):
    """Schema para la respuesta de una visita"""
    id: str
    visited_user_email: EmailStr
    visitor_email: EmailStr
    visitor_oauth_id: str
    visited_at: datetime
