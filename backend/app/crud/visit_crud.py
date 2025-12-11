from app.models.visit import Visit
from pydantic import EmailStr
from typing import List


class VisitCRUD:
    """
    CRUD operations para Visit
    """
    
    @staticmethod
    async def create_visit(
        visited_user_email: EmailStr,
        visitor_email: EmailStr,
        visitor_oauth_id: str
    ) -> Visit:
        """Registra una nueva visita al mapa de un usuario"""
        visit = Visit(
            visited_user_email=visited_user_email,
            visitor_email=visitor_email,
            visitor_oauth_id=visitor_oauth_id
        )
        await visit.insert()
        return visit
    
    @staticmethod
    async def get_user_visits(user_email: EmailStr, limit: int = 50) -> List[Visit]:
        """
        Obtiene las visitas recibidas por un usuario
        Ordenadas de más reciente a más antigua
        """
        visits = await Visit.find(
            Visit.visited_user_email == user_email
        ).sort(-Visit.visited_at).limit(limit).to_list()
        return visits
