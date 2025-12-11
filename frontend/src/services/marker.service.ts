// Servicio de marcadores para MiMapa
import type { Marker, MarkerCreate, UserMapResponse } from '@/interfaces/mimapa';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class MarkerService {
  /**
   * Comprime una imagen antes de convertirla a base64
   */
  private async compressImage(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target?.result as string;
        img.onload = () => {
          const canvas = document.createElement('canvas');
          const MAX_WIDTH = 800;
          const MAX_HEIGHT = 800;
          let width = img.width;
          let height = img.height;

          // Calcular nuevas dimensiones manteniendo aspecto
          if (width > height) {
            if (width > MAX_WIDTH) {
              height *= MAX_WIDTH / width;
              width = MAX_WIDTH;
            }
          } else {
            if (height > MAX_HEIGHT) {
              width *= MAX_HEIGHT / height;
              height = MAX_HEIGHT;
            }
          }

          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx?.drawImage(img, 0, 0, width, height);

          // Comprimir a JPEG con calidad 0.7
          const compressedBase64 = canvas.toDataURL('image/jpeg', 0.7);
          resolve(compressedBase64);
        };
        img.onerror = reject;
      };
      reader.onerror = reject;
    });
  }

  /**
   * Crea un nuevo marcador con imagen opcional
   */
  async createMarker(
    data: MarkerCreate,
    imageFile?: File
  ): Promise<Marker> {
    // Si hay imagen, comprimirla y convertirla a base64
    let image_url: string | undefined = undefined;
    if (imageFile) {
      image_url = await this.compressImage(imageFile);
    }

    const payload = {
      location_name: data.location_name,
      description: data.description || null,
      image_url: image_url || null,
    };

    const response = await fetch(`${API_URL}/markers/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authService.getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al crear marcador' }));
      throw new Error(error.detail || 'Error al crear marcador');
    }

    return await response.json();
  }

  /**
   * Obtiene todos los marcadores del usuario actual
   */
  async getMyMarkers(): Promise<Marker[]> {
    const response = await fetch(`${API_URL}/markers/my-markers`, {
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al obtener marcadores');
    }

    return await response.json();
  }

  /**
   * Obtiene el mapa de un usuario por su email
   */
  async getUserMap(email: string): Promise<UserMapResponse> {
    const response = await fetch(`${API_URL}/markers/user/${encodeURIComponent(email)}`, {
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Usuario no encontrado' }));
      throw new Error(error.detail || 'Error al obtener mapa del usuario');
    }

    return await response.json();
  }

  /**
   * Elimina un marcador
   */
  async deleteMarker(markerId: string): Promise<void> {
    const response = await fetch(`${API_URL}/markers/${markerId}`, {
      method: 'DELETE',
      headers: authService.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al eliminar marcador');
    }
  }

  /**
   * Actualiza la imagen de un marcador
   */
  async updateMarkerImage(markerId: string, imageFile: File): Promise<Marker> {
    const formData = new FormData();
    formData.append('image', imageFile);

    const response = await fetch(`${API_URL}/markers/${markerId}/image`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authService.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Error al actualizar imagen');
    }

    return await response.json();
  }
}

export default new MarkerService();
