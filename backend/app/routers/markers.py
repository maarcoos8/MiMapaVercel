from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from app.models.user import User
from app.models.marker import Marker
from app.schemas.marker import MarkerCreate, MarkerUpdate
from app.crud.marker_crud import MarkerCRUD
from app.crud.visit_crud import VisitCRUD
from app.core.auth import get_current_user, get_current_user_optional
from app.core.geocoding import geocode_location
from beanie import PydanticObjectId
import cloudinary
import cloudinary.uploader
from app.core.config import settings
import logging

router = APIRouter(prefix="/markers", tags=["Markers"])

# Configurar Cloudinary (obligatorio)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


async def upload_image_to_cloudinary(file: UploadFile) -> str:
    """Sube una imagen a Cloudinary y retorna la URL"""
    try:
        # Leer el contenido del archivo
        contents = await file.read()
        
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="mimapa",
            resource_type="image"
        )
        
        return result['secure_url']
    except Exception as e:
        logging.error(f"Error subiendo imagen a Cloudinary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la imagen"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_marker(
    marker_data: MarkerCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo marcador para el usuario autenticado
    - Geocodifica la ubicación para obtener coordenadas
    - La imagen debe venir como URL de Cloudinary o base64 (se convertirá a Cloudinary)
    """
    # Geocodificar la ubicación
    coordinates = await geocode_location(marker_data.location_name)
    if not coordinates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se pudieron encontrar coordenadas para: {marker_data.location_name}"
        )
    
    latitude, longitude = coordinates
    
    # Procesar image_url: si viene como base64, subir a Cloudinary
    image_url = marker_data.image_url
    if image_url and image_url.startswith('data:image'):
        try:
            result = cloudinary.uploader.upload(image_url, folder="mimapa")
            image_url = result['secure_url']
        except Exception as e:
            logging.error(f"Error subiendo imagen base64 a Cloudinary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al procesar la imagen"
            )
    
    # Crear marcador
    marker = await MarkerCRUD.create_marker(
        user_email=current_user.email,
        location_name=marker_data.location_name,
        latitude=latitude,
        longitude=longitude,
        image_url=image_url,
        description=marker_data.description
    )
    
    # Serializar con id explícito
    marker_dict = marker.model_dump(by_alias=True)
    marker_dict['id'] = str(marker.id)
    return marker_dict


@router.get("/my-markers")
async def get_my_markers(current_user: User = Depends(get_current_user)):
    """Obtiene todos los marcadores del usuario autenticado"""
    markers = await MarkerCRUD.get_user_markers(current_user.email)
    # Serializar con id explícito
    return [
        {**m.model_dump(by_alias=True), 'id': str(m.id)} for m in markers
    ]


@router.get("/user/{email}")
async def get_user_map(email: str, current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Obtiene el mapa de otro usuario (solo lectura)
    Permite visualizar los marcadores de otros usuarios ingresando su email
    Registra la visita si el usuario está autenticado
    """
    # Buscar el usuario
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró un usuario con el email: {email}"
        )
    
    # Registrar la visita si hay usuario autenticado y no es el dueño del mapa
    if current_user and current_user.email != email:
        await VisitCRUD.create_visit(
            visited_user_email=email,
            visitor_email=current_user.email,
            visitor_oauth_id=current_user.oauth_id
        )
    
    # Obtener marcadores del usuario
    markers = await MarkerCRUD.get_user_markers(email)
    
    # Serializar con id explícito
    markers_data = [
        {**m.model_dump(by_alias=True), 'id': str(m.id)} for m in markers
    ]
    
    return {
        "user_email": user.email,
        "user_name": user.name,
        "markers": markers_data
    }


@router.delete("/{marker_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_marker(
    marker_id: str,
    current_user: User = Depends(get_current_user)
):
    """Elimina un marcador del usuario autenticado"""
    try:
        object_id = PydanticObjectId(marker_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de marcador inválido"
        )
    
    deleted = await MarkerCRUD.delete_marker(object_id, current_user.email)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marcador no encontrado o no autorizado"
        )
    
    return None


@router.put("/{marker_id}")
async def update_marker(
    marker_id: str,
    marker_data: MarkerUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualiza un marcador del usuario autenticado"""
    try:
        object_id = PydanticObjectId(marker_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de marcador inválido"
        )
    
    marker = await Marker.get(object_id)
    if not marker or marker.user_email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marcador no encontrado o no autorizado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = marker_data.model_dump(exclude_unset=True)
    
    # Si se actualiza location_name, recalcular coordenadas
    if "location_name" in update_data:
        coordinates = await geocode_location(update_data["location_name"])
        if not coordinates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se pudieron encontrar coordenadas para: {update_data['location_name']}"
            )
        marker.latitude, marker.longitude = coordinates
        marker.location_name = update_data["location_name"]
    
    if "description" in update_data:
        marker.description = update_data["description"]
    
    await marker.save()
    
    # Serializar con id explícito
    marker_dict = marker.model_dump(by_alias=True)
    marker_dict['id'] = str(marker.id)
    return marker_dict


@router.put("/{marker_id}/image")
async def update_marker_image(
    marker_id: str,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Actualiza la imagen de un marcador existente (siempre sube a Cloudinary)"""
    try:
        object_id = PydanticObjectId(marker_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de marcador inválido"
        )
    
    # Subir imagen a Cloudinary
    image_url = await upload_image_to_cloudinary(image)
    
    # Actualizar marcador
    marker = await MarkerCRUD.update_marker_image(object_id, current_user.email, image_url)
    if not marker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marcador no encontrado o no autorizado"
        )
    
    # Serializar con id explícito
    marker_dict = marker.model_dump(by_alias=True)
    marker_dict['id'] = str(marker.id)
    return marker_dict
