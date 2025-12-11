from app.models.marker import Marker
from pydantic import EmailStr
from typing import List, Optional
from beanie import PydanticObjectId


class MarkerCRUD:
    """
    CRUD operations para Marker
    """
    
    @staticmethod
    async def create_marker(
        user_email: EmailStr,
        location_name: str,
        latitude: float,
        longitude: float,
        image_url: Optional[str] = None,
        description: Optional[str] = None
    ) -> Marker:
        """Crea un nuevo marcador para el usuario"""
        marker = Marker(
            user_email=user_email,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            image_url=image_url,
            description=description
        )
        await marker.insert()
        return marker
    
    @staticmethod
    async def get_user_markers(user_email: EmailStr) -> List[Marker]:
        """Obtiene todos los marcadores de un usuario"""
        markers = await Marker.find(Marker.user_email == user_email).to_list()
        return markers
    
    @staticmethod
    async def get_marker_by_id(marker_id: PydanticObjectId) -> Optional[Marker]:
        """Obtiene un marcador por su ID"""
        marker = await Marker.get(marker_id)
        return marker
    
    @staticmethod
    async def delete_marker(marker_id: PydanticObjectId, user_email: EmailStr) -> bool:
        """
        Elimina un marcador si pertenece al usuario
        Retorna True si se eliminó, False si no existe o no pertenece al usuario
        """
        marker = await Marker.get(marker_id)
        if not marker or marker.user_email != user_email:
            return False
        
        await marker.delete()
        return True
    
    @staticmethod
    async def update_marker_image(
        marker_id: PydanticObjectId,
        user_email: EmailStr,
        image_url: str
    ) -> Optional[Marker]:
        """
        Actualiza la imagen de un marcador
        Retorna el marcador actualizado o None si no existe/no pertenece al usuario
        """
        marker = await Marker.get(marker_id)
        if not marker or marker.user_email != user_email:
            return None
        
        marker.image_url = image_url
        await marker.save()
        return marker
