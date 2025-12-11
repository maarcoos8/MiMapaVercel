// Servicio de visitas para MiMapa
import type { Visit } from '@/interfaces/mimapa';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class VisitService {
  /**
   * Obtiene las visitas recibidas por el usuario actual
   */
  async getMyVisits(): Promise<Visit[]> {
    const response = await fetch(`${API_URL}/visits/my-visits`, {
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al obtener visitas');
    }

    return await response.json();
  }

  /**
   * Registra una visita al mapa de otro usuario
   */
  async registerVisit(visitedUserEmail: string): Promise<Visit> {
    const response = await fetch(`${API_URL}/visits/register`, {
      method: 'POST',
      headers: {
        ...authService.getAuthHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ visited_user_email: visitedUserEmail }),
    });

    if (!response.ok) {
      throw new Error('Error al registrar visita');
    }

    return await response.json();
  }
}

export default new VisitService();
