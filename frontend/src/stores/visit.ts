// Store de visitas para MiMapa
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { Visit } from '@/interfaces/mimapa';
import visitService from '@/services/visit.service';

export const useVisitStore = defineStore('visit', () => {
  const myVisits = ref<Visit[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Carga las visitas recibidas por el usuario actual
   */
  async function loadMyVisits(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      myVisits.value = await visitService.getMyVisits();
    } catch (err: any) {
      error.value = err.message || 'Error al cargar visitas';
      myVisits.value = [];
    } finally {
      loading.value = false;
    }
  }

  /**
   * Limpia las visitas del store
   */
  function clearVisits(): void {
    myVisits.value = [];
  }

  return {
    myVisits,
    loading,
    error,
    loadMyVisits,
    clearVisits,
  };
});
