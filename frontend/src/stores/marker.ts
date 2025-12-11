// Store de marcadores para MiMapa
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Marker, MarkerCreate, UserMapResponse } from '@/interfaces/mimapa';
import markerService from '@/services/marker.service';

export const useMarkerStore = defineStore('marker', () => {
  const myMarkers = ref<Marker[]>([]);
  const visitedUserMap = ref<UserMapResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastFetch = ref<number>(0);

  // Cache: evitar fetch si se cargó hace menos de 5 minutos
  const CACHE_DURATION = 5 * 60 * 1000;

  /**
   * Carga los marcadores del usuario actual
   */
  async function loadMyMarkers(force = false): Promise<void> {
    const now = Date.now();
    if (!force && myMarkers.value.length > 0 && now - lastFetch.value < CACHE_DURATION) {
      return; // Usar caché
    }

    loading.value = true;
    error.value = null;

    try {
      myMarkers.value = await markerService.getMyMarkers();
      lastFetch.value = now;
    } catch (err: any) {
      error.value = err.message || 'Error al cargar marcadores';
      myMarkers.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * Crea un nuevo marcador
   */
  async function createMarker(data: MarkerCreate, imageFile?: File): Promise<Marker> {
    loading.value = true;
    error.value = null;

    try {
      const newMarker = await markerService.createMarker(data, imageFile);
      myMarkers.value.push(newMarker);
      return newMarker;
    } catch (err: any) {
      error.value = err.message || 'Error al crear marcador';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Elimina un marcador
   */
  async function deleteMarker(markerId: string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await markerService.deleteMarker(markerId);
      myMarkers.value = myMarkers.value.filter((m) => m.id !== markerId);
    } catch (err: any) {
      error.value = err.message || 'Error al eliminar marcador';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Actualiza la imagen de un marcador
   */
  async function updateMarkerImage(markerId: string, imageFile: File): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      const updatedMarker = await markerService.updateMarkerImage(markerId, imageFile);
      const index = myMarkers.value.findIndex((m) => m.id === markerId);
      if (index !== -1) {
        myMarkers.value[index] = updatedMarker;
      }
    } catch (err: any) {
      error.value = err.message || 'Error al actualizar imagen';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Carga el mapa de otro usuario
   */
  async function loadUserMap(email: string): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      visitedUserMap.value = await markerService.getUserMap(email);
    } catch (err: any) {
      error.value = err.message || 'Error al cargar mapa del usuario';
      visitedUserMap.value = null;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Limpia el caché de marcadores
   */
  function clearCache(): void {
    myMarkers.value = [];
    visitedUserMap.value = null;
    lastFetch.value = 0;
  }

  /**
   * Limpia el mapa visitado
   */
  function clearVisitedMap(): void {
    visitedUserMap.value = null;
  }

  return {
    myMarkers,
    visitedUserMap,
    loading,
    error,
    loadMyMarkers,
    createMarker,
    deleteMarker,
    updateMarkerImage,
    loadUserMap,
    clearCache,
    clearVisitedMap,
  };
});
