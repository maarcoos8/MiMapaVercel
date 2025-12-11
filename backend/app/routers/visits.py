from fastapi import APIRouter, Depends
from typing import List
from app.models.user import User
from app.models.visit import Visit
from app.crud.visit_crud import VisitCRUD
from app.core.auth import get_current_user

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.get("/my-visits")
async def get_my_visits(current_user: User = Depends(get_current_user)):
    """
    Obtiene las visitas recibidas al mapa del usuario actual
    Ordenadas de más reciente a más antigua
    """
    visits = await VisitCRUD.get_user_visits(current_user.email)
    
    # Serializar con id explícito
    return [
        {**v.model_dump(by_alias=True), 'id': str(v.id)} for v in visits
    ]


@router.post("/register")
async def register_visit(
    visited_user_email: str,
    current_user: User = Depends(get_current_user)
):
    """
    Registra una visita al mapa de otro usuario
    Solo se registra si el visitante no es el dueño del mapa
    """
    # No registrar si el usuario visita su propio mapa
    if current_user.email == visited_user_email:
        return {"message": "No se registra visita a tu propio mapa"}
    
    # Registrar la visita
    visit = await VisitCRUD.create_visit(
        visited_user_email=visited_user_email,
        visitor_email=current_user.email,
        visitor_oauth_id=current_user.oauth_id
    )
    
    # Serializar con id explícito
    visit_dict = visit.model_dump(by_alias=True)
    visit_dict['id'] = str(visit.id)
    return visit_dict
