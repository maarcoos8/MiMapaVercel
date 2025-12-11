<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Mi Mapa</ion-title>
        <ion-buttons slot="end">
          <ion-button @click="logout">
            <ion-icon slot="icon-only" :icon="logOutOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div v-if="loading" class="loading-container">
        <ion-spinner></ion-spinner>
        <p>Cargando tu mapa...</p>
      </div>

      <div v-else-if="error" class="error-container">
        <ion-icon :icon="alertCircleOutline" class="error-icon"></ion-icon>
        <p>{{ error }}</p>
        <ion-button @click="loadMarkers">Reintentar</ion-button>
      </div>

      <div v-else class="content-layout">
        <!-- Buscador de mapas de otros usuarios -->
        <div class="search-section">
          <div class="search-controls">
            <ion-searchbar
              v-model="searchEmail"
              placeholder="Buscar mapa de otro usuario por email"
              :debounce="500"
              @ionChange="handleSearchChange"
              @ionClear="clearSearch"
            ></ion-searchbar>
            <ion-button 
              v-if="visitingUser"
              color="primary"
              @click="clearSearch"
              class="back-button"
            >
              <ion-icon slot="start" :icon="homeOutline"></ion-icon>
              Volver a mi mapa
            </ion-button>
          </div>
          <div v-if="visitingUser" class="visiting-banner">
            <ion-icon :icon="personCircleOutline"></ion-icon>
            <span>Viendo el mapa de: <strong>{{ visitingUser }}</strong></span>
            <ion-button size="small" fill="clear" @click="clearSearch">
              <ion-icon slot="icon-only" :icon="closeOutline"></ion-icon>
            </ion-button>
          </div>
        </div>

        <div class="map-container">
          <!-- Panel izquierdo: Lista de marcadores -->
          <div class="markers-panel">
            <div v-if="currentMarkers.length > 0" class="markers-list">
              <h3>{{ visitingUser ? `Lugares de ${visitingUser}` : 'Tus lugares' }} ({{ currentMarkers.length }})</h3>
              <div class="marker-items">
                <div 
                  v-for="marker in currentMarkers" 
                  :key="marker.id"
                  class="marker-item"
                  @click="focusMarker(marker)"
                >
                  <div class="marker-image">
                    <img 
                      v-if="marker.image_url" 
                      :src="marker.image_url" 
                      :alt="marker.location_name"
                    />
                    <div v-else class="no-image">
                      <ion-icon :icon="imageOutline"></ion-icon>
                    </div>
                  </div>
                  <div class="marker-details">
                    <h4>{{ marker.location_name }}</h4>
                    <p v-if="marker.description" class="description">{{ marker.description }}</p>
                    <p class="date">{{ formatDate(marker.created_at) }}</p>
                  </div>
                  <ion-button 
                    v-if="!visitingUser"
                    size="small" 
                    fill="clear" 
                    color="danger"
                    @click.stop="confirmDelete(marker)"
                  >
                    <ion-icon slot="icon-only" :icon="trashOutline"></ion-icon>
                  </ion-button>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              <ion-icon :icon="mapOutline" class="empty-icon"></ion-icon>
              <h2>No tienes marcadores aún</h2>
              <p>Empieza a añadir lugares que has visitado</p>
              <ion-button @click="goToAddMarker">
                <ion-icon slot="start" :icon="addOutline"></ion-icon>
                Añadir mi primer lugar
              </ion-button>
            </div>
          </div>

          <!-- Panel derecho: Mapa -->
          <div class="map-wrapper">
            <MapViewer 
              :markers="currentMarkers" 
              @marker-click="handleMarkerClick"
              ref="mapViewerRef"
            />
          </div>
        </div>

        <!-- Lista de visitas recibidas (solo si no estamos viendo el mapa de otro usuario) -->
        <div v-if="!visitingUser && visits.length > 0" class="visits-section">
          <h3>Visitas a tu mapa ({{ visits.length }})</h3>
          <div class="visits-list">
            <div v-for="visit in visits" :key="visit.id" class="visit-item">
              <div class="visit-info">
                <div class="visit-email">
                  <ion-icon :icon="personOutline"></ion-icon>
                  <strong>{{ visit.visitor_email }}</strong>
                </div>
                <div class="visit-meta">
                  <span class="visit-date">
                    <ion-icon :icon="timeOutline"></ion-icon>
                    {{ formatDateTime(visit.visited_at) }}
                  </span>
                  <span class="visit-oauth">OAuth ID: {{ visit.visitor_oauth_id }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón flotante para añadir marcador (solo si no estamos viendo el mapa de otro usuario) -->
        <ion-fab v-if="!visitingUser" vertical="bottom" horizontal="end" slot="fixed">
          <ion-fab-button @click="goToAddMarker">
            <ion-icon :icon="addOutline"></ion-icon>
          </ion-fab-button>
        </ion-fab>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonButtons,
  IonIcon,
  IonSpinner,
  IonFab,
  IonFabButton,
  IonSearchbar,
  alertController,
} from '@ionic/vue';
import {
  logOutOutline,
  addOutline,
  alertCircleOutline,
  mapOutline,
  imageOutline,
  trashOutline,
  personCircleOutline,
  closeOutline,
  personOutline,
  timeOutline,
  homeOutline,
} from 'ionicons/icons';
import { onMounted, computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useMarkerStore } from '@/stores/marker';
import { useVisitStore } from '@/stores/visit';
import MapViewer from '@/components/MapViewer.vue';
import type { Marker } from '@/interfaces/mimapa';

const router = useRouter();
const authStore = useAuthStore();
const markerStore = useMarkerStore();
const visitStore = useVisitStore();
const mapViewerRef = ref<InstanceType<typeof MapViewer> | null>(null);

const searchEmail = ref('');
const visitingUser = ref('');

const loading = computed(() => markerStore.loading);
const error = computed(() => markerStore.error);
const visits = computed(() => visitStore.myVisits);

const currentMarkers = computed(() => {
  if (visitingUser.value) {
    return markerStore.visitedUserMap?.markers || [];
  }
  return markerStore.myMarkers;
});

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
}

function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function loadMarkers() {
  await markerStore.loadMyMarkers(true);
}

async function handleSearchChange(event: CustomEvent) {
  const email = event.detail.value?.trim();
  if (!email) {
    clearSearch();
    return;
  }
  
  // Validar que sea un email completo
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (emailRegex.test(email)) {
    try {
      await markerStore.loadUserMap(email);
      visitingUser.value = email;
      searchEmail.value = ''; // Limpiar el campo de búsqueda
    } catch (err) {
      console.error('Error cargando mapa del usuario:', err);
      visitingUser.value = '';
    }
  }
}

function clearSearch() {
  searchEmail.value = '';
  visitingUser.value = '';
  markerStore.clearVisitedMap();
}

function goToAddMarker() {
  router.push('/add-marker');
}

function handleMarkerClick(marker: Marker) {
  console.log('Marker clicked:', marker);
}

function focusMarker(marker: Marker) {
  console.log('Focusing marker:', marker.id);
  // Abrir el popup del marcador en el mapa
  if (mapViewerRef.value && typeof mapViewerRef.value === 'object' && 'openMarkerPopup' in mapViewerRef.value) {
    (mapViewerRef.value as { openMarkerPopup: (id: string) => void }).openMarkerPopup(marker.id);
  }
}

async function confirmDelete(marker: Marker) {
  const alert = await alertController.create({
    header: 'Eliminar marcador',
    message: `¿Estás seguro de eliminar "${marker.location_name}"?`,
    buttons: [
      {
        text: 'Cancelar',
        role: 'cancel',
      },
      {
        text: 'Eliminar',
        role: 'destructive',
        handler: async () => {
          try {
            await markerStore.deleteMarker(marker.id);
          } catch (err) {
            console.error('Error al eliminar:', err);
          }
        },
      },
    ],
  });

  await alert.present();
}

async function logout() {
  const alert = await alertController.create({
    header: 'Cerrar sesión',
    message: '¿Estás seguro de cerrar sesión?',
    buttons: [
      {
        text: 'Cancelar',
        role: 'cancel',
      },
      {
        text: 'Salir',
        handler: async () => {
          await authStore.logout();
          markerStore.clearCache();
          router.push('/login');
        },
      },
    ],
  });

  await alert.present();
}

onMounted(async () => {
  console.log('MyMap mounted');
  console.log('isAuthenticated:', authStore.isAuthenticated);
  if (!authStore.isAuthenticated) {
    console.log('Not authenticated, redirecting to login');
    router.push('/login');
    return;
  }
  console.log('Loading markers...');
  await loadMarkers();
  await visitStore.loadMyVisits();
  console.log('Markers and visits loaded');
  console.log('Markers loaded:', markerStore.myMarkers.length);
});
</script>

<style scoped>
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  gap: 1rem;
  padding: 2rem;
}

.error-icon {
  font-size: 64px;
  color: var(--ion-color-danger);
}

.content-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
}

.search-section {
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.search-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-controls ion-searchbar {
  flex: 1;
}

.back-button {
  flex-shrink: 0;
  white-space: nowrap;
}

.visiting-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--ion-color-primary);
  color: white;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.visiting-banner ion-icon {
  font-size: 1.5rem;
}

.map-container {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1rem;
  height: 600px;
  flex-shrink: 0;
  overflow: hidden;
}

.markers-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 12px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.markers-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.markers-list h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  color: var(--ion-color-dark);
  font-size: 1.1em;
}

.marker-items {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.marker-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  transition: all 0.2s;
}

.marker-item:hover {
  background: #f0f0f0;
  transform: translateX(4px);
}

.marker-image {
  width: 60px;
  height: 60px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
}

.marker-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.marker-image .no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e0e0e0;
  color: #999;
}

.marker-image .no-image ion-icon {
  font-size: 24px;
}

.marker-details {
  flex: 1;
  min-width: 0;
}

.marker-details h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.95em;
  font-weight: 600;
  color: var(--ion-color-dark);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.marker-details .description {
  margin: 0 0 0.25rem 0;
  font-size: 0.85em;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.marker-details .date {
  margin: 0;
  font-size: 0.75em;
  color: #999;
}

.map-wrapper {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  color: var(--ion-color-medium);
  margin-bottom: 1rem;
}

.empty-state h2 {
  color: var(--ion-color-dark);
  margin: 0.5rem 0;
}

.empty-state p {
  color: var(--ion-color-medium);
  margin-bottom: 2rem;
}

.visits-section {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.visits-section h3 {
  margin: 0 0 1rem 0;
  color: var(--ion-color-dark);
  font-size: 1.1em;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.75rem;
}

.visits-list {
  max-height: 300px;
  overflow-y: auto;
}

.visit-item {
  padding: 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.visit-item:last-child {
  border-bottom: none;
}

.visit-item:hover {
  background: #f9f9f9;
}

.visit-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.visit-email {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ion-color-dark);
  font-size: 0.95em;
}

.visit-email ion-icon {
  font-size: 1.2em;
  color: var(--ion-color-primary);
}

.visit-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85em;
  color: #666;
  margin-left: 1.7rem;
}

.visit-date {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.visit-date ion-icon {
  font-size: 1em;
}

.visit-oauth {
  color: #999;
  font-size: 0.9em;
}
</style>
