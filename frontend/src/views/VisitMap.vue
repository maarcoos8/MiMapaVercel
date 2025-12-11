<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/my-map"></ion-back-button>
        </ion-buttons>
        <ion-title>Visitar Mapa</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <!-- Formulario de búsqueda -->
      <div v-if="!visitedUserMap" class="search-section">
        <h2>Buscar mapa de usuario</h2>
        <p class="info-text">Ingresa el email del usuario para ver su mapa</p>

        <form @submit.prevent="searchUser">
          <ion-item>
            <ion-input
              label="Email del usuario"
              label-placement="floating"
              v-model="searchEmail"
              type="email"
              placeholder="usuario@ejemplo.com"
              required
            ></ion-input>
          </ion-item>

          <ion-button
            expand="block"
            type="submit"
            :disabled="!searchEmail || loading"
            class="search-button"
          >
            <ion-spinner v-if="loading" name="crescent"></ion-spinner>
            <span v-else>
              <ion-icon slot="start" :icon="searchOutline"></ion-icon>
              Buscar
            </span>
          </ion-button>
        </form>

        <ion-text v-if="error" color="danger" class="error-text">
          <p>{{ error }}</p>
        </ion-text>
      </div>

      <!-- Mapa del usuario visitado -->
      <div v-else class="user-map-container">
        <div class="user-info">
          <h2>{{ visitedUserMap.user_name }}</h2>
          <p>{{ visitedUserMap.user_email }}</p>
          <p class="markers-count">
            {{ visitedUserMap.markers.length }} 
            {{ visitedUserMap.markers.length === 1 ? 'lugar visitado' : 'lugares visitados' }}
          </p>
          <ion-button size="small" fill="outline" @click="resetSearch">
            <ion-icon slot="start" :icon="arrowBackOutline"></ion-icon>
            Buscar otro usuario
          </ion-button>
        </div>

        <div class="map-wrapper">
          <MapViewer 
            v-if="visitedUserMap.markers.length > 0"
            :markers="visitedUserMap.markers"
            @marker-click="handleMarkerClick"
          />
          <div v-else class="empty-map">
            <ion-icon :icon="mapOutline" class="empty-icon"></ion-icon>
            <p>Este usuario no tiene marcadores aún</p>
          </div>
        </div>

        <!-- Galería de imágenes del usuario -->
        <div v-if="visitedUserMap.markers.length > 0" class="images-gallery">
          <h3>Lugares de {{ visitedUserMap.user_name }}</h3>
          <div class="images-grid">
            <div 
              v-for="marker in visitedUserMap.markers" 
              :key="marker.id"
              class="image-card"
            >
              <img 
                v-if="marker.image_url" 
                :src="marker.image_url" 
                :alt="marker.location_name"
              />
              <div v-else class="no-image">
                <ion-icon :icon="imageOutline"></ion-icon>
              </div>
              <div class="image-info">
                <p class="location-name">{{ marker.location_name }}</p>
                <p v-if="marker.description" class="description">
                  {{ marker.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
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
  IonBackButton,
  IonIcon,
  IonInput,
  IonItem,
  IonSpinner,
  IonText,
} from '@ionic/vue';
import { searchOutline, arrowBackOutline, mapOutline, imageOutline } from 'ionicons/icons';
import { ref, computed } from 'vue';
import { useMarkerStore } from '@/stores/marker';
import MapViewer from '@/components/MapViewer.vue';
import type { Marker } from '@/interfaces/mimapa';

const markerStore = useMarkerStore();
const searchEmail = ref('');
const loading = ref(false);
const error = ref<string | null>(null);

const visitedUserMap = computed(() => markerStore.visitedUserMap);

async function searchUser() {
  if (!searchEmail.value) return;

  loading.value = true;
  error.value = null;

  try {
    await markerStore.loadUserMap(searchEmail.value);
  } catch (err: any) {
    error.value = err.message || 'Usuario no encontrado';
  } finally {
    loading.value = false;
  }
}

function resetSearch() {
  searchEmail.value = '';
  error.value = null;
  markerStore.visitedUserMap = null;
}

function handleMarkerClick(marker: Marker) {
  console.log('Marker clicked:', marker);
}
</script>

<style scoped>
.search-section {
  max-width: 500px;
  margin: 2rem auto;
}

.search-section h2 {
  text-align: center;
  color: var(--ion-color-primary);
  margin-bottom: 0.5rem;
}

.info-text {
  text-align: center;
  color: var(--ion-color-medium);
  margin-bottom: 2rem;
}

.search-button {
  margin-top: 1rem;
}

.error-text {
  display: block;
  margin-top: 1rem;
  text-align: center;
}

.user-map-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.user-info {
  padding: 1rem;
  background: var(--ion-color-light);
  text-align: center;
}

.user-info h2 {
  margin: 0;
  color: var(--ion-color-primary);
}

.user-info p {
  margin: 0.25rem 0;
  color: var(--ion-color-medium);
}

.markers-count {
  font-weight: 600;
  color: var(--ion-color-dark) !important;
  margin: 0.5rem 0 1rem 0 !important;
}

.map-wrapper {
  flex: 1;
  position: relative;
}

.empty-map {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--ion-color-medium);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 1rem;
}

.images-gallery {
  background: white;
  padding: 1rem;
  border-top: 1px solid var(--ion-color-light);
  max-height: 40%;
  overflow-y: auto;
}

.images-gallery h3 {
  margin: 0 0 1rem 0;
  color: var(--ion-color-dark);
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-card {
  border-radius: 8px;
  overflow: hidden;
  background: var(--ion-color-light);
}

.image-card img,
.no-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ion-color-light);
  color: var(--ion-color-medium);
}

.no-image ion-icon {
  font-size: 40px;
}

.image-info {
  padding: 0.75rem;
}

.location-name {
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: var(--ion-color-dark);
}

.description {
  font-size: 0.875rem;
  margin: 0;
  color: var(--ion-color-medium);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
