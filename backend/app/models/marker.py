from beanie import Document, PydanticObjectId
from pydantic import EmailStr, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime


class Marker(Document):
    """
    Modelo de Marcador para el mapa del usuario
    Almacena países/ciudades visitadas con coordenadas e imágenes
    """
    id: Optional[PydanticObjectId] = Field(default=None, alias="_id")
    user_email: EmailStr = Field(..., index=True)  # Email del usuario propietario
    location_name: str  # Nombre del país o ciudad
    latitude: float  # Coordenada latitud
    longitude: float  # Coordenada longitud
    image_url: Optional[str] = None  # URL de la imagen (Cloudinary o almacenada)
    description: Optional[str] = None  # Descripción opcional del lugar
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={PydanticObjectId: str},
        json_schema_extra={
            "example": {
                "user_email": "user@example.com",
                "location_name": "Paris, France",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "image_url": "https://res.cloudinary.com/demo/image/upload/paris.jpg",
                "description": "Visited the Eiffel Tower"
            }
        }
    )
    
    class Settings:
        name = "markers"
