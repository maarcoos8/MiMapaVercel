from beanie import Document, PydanticObjectId
from pydantic import EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class Visit(Document):
    """
    Modelo de Visita al mapa de un usuario
    Registra cuándo un usuario visita el mapa de otro usuario
    """
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    visited_user_email: EmailStr = Field(..., index=True)  # Email del usuario cuyo mapa fue visitado
    visitor_email: EmailStr  # Email del visitante
    visitor_oauth_id: str  # Token OAuth del visitante
    visited_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "visited_user_email": "user@example.com",
                "visitor_email": "visitor@example.com",
                "visitor_oauth_id": "google_123456789",
                "visited_at": "2025-12-11T17:00:00Z"
            }
        }
    )
    
    class Settings:
        name = "visits"
