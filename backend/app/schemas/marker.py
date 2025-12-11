from pydantic import BaseModel, Field
from typing import Optional

# Schema para crear marcadores
class MarkerCreate(BaseModel):
    location_name: str = Field(..., min_length=1, max_length=200, description="Nombre del país o ciudad")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del lugar visitado")
    image_url: Optional[str] = Field(None, description="URL de la imagen (base64 o URL de Cloudinary)")

# Schema para actualizar marcadores
class MarkerUpdate(BaseModel):
    location_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Nombre del país o ciudad")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción del lugar visitado")
