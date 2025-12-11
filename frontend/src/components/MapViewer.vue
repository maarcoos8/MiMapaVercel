<template>
  <div class="map-viewer">
    <div ref="mapEl" class="map"></div>
    
    <!-- Panel de información del marcador seleccionado -->
    <div v-if="selectedMarker" class="marker-info">
      <div class="marker-info-content">
        <h3>{{ selectedMarker.location_name }}</h3>
        <p v-if="selectedMarker.description" class="description">
          {{ selectedMarker.description }}
        </p>
        <p class="coordinates">
          {{ selectedMarker.latitude.toFixed(4) }}, {{ selectedMarker.longitude.toFixed(4) }}
        </p>
        <p class="date">{{ formatDate(selectedMarker.created_at) }}</p>
        <ion-button size="small" fill="clear" @click="closeInfo">
          Cerrar
        </ion-button>
      </div>
      <img v-if="selectedMarker.image_url" :src="selectedMarker.image_url" alt="Foto del lugar" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue';
import { IonButton } from '@ionic/vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Marker } from '@/interfaces/mimapa';

// Fix Leaflet icon paths for Vite
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl,
  shadowUrl
});

// Definición del icono personalizado
const defaultIcon = L.icon({
  iconUrl: String(iconUrl),
  iconRetinaUrl: String(iconRetinaUrl),
  shadowUrl: String(shadowUrl),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const props = defineProps<{
  markers: Marker[];
  center?: { lat: number; lon: number };
  zoom?: number;
}>();

const emit = defineEmits<{
  markerClick: [marker: Marker];
}>();

const mapEl = ref<HTMLElement | null>(null);
const selectedMarker = ref<Marker | null>(null);
let map: L.Map | null = null;
const markerLayers = new Map<string, L.Marker>();

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

function closeInfo() {
  selectedMarker.value = null;
}

// Exponer método para abrir popup de un marcador específico
function openMarkerPopup(markerId: string) {
  console.log('Opening popup for marker:', markerId);
  console.log('Available markers:', Array.from(markerLayers.keys()));
  const markerLayer = markerLayers.get(markerId);
  if (markerLayer && map) {
    console.log('Marker layer found, opening popup');
    map.setView(markerLayer.getLatLng(), 15, { animate: true });
    setTimeout(() => {
      markerLayer.openPopup();
    }, 300);
  } else {
    console.error('Marker layer not found for ID:', markerId);
  }
}

// Exponer el método para que el componente padre pueda acceder
defineExpose({
  openMarkerPopup
});

function initMap() {
  if (!mapEl.value) return;

  const defaultLat = props.center?.lat || 40.4168;
  const defaultLon = props.center?.lon || -3.7038;
  const defaultZoom = props.zoom || 3;

  map = L.map(mapEl.value).setView([defaultLat, defaultLon], defaultZoom);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19
  }).addTo(map);

  // Forzar recalcular el tamaño del mapa después de renderizar
  setTimeout(() => {
    if (map) {
      map.invalidateSize();
      updateMarkers();
    }
  }, 100);
}

function updateMarkers() {
  if (!map) return;

  // Limpiar marcadores existentes
  markerLayers.forEach(marker => marker.remove());
  markerLayers.clear();

  // Añadir marcadores
  props.markers.forEach(marker => {
    const leafletMarker = L.marker([marker.latitude, marker.longitude], {
      icon: defaultIcon
    }).addTo(map!);

    // Crear contenido del popup con imagen si existe
    let popupContent = `<div style="max-width: 250px; min-width: 200px;">
      <h4 style="margin: 0 0 8px 0; font-size: 1em; color: #333;">${marker.location_name}</h4>`;
    
    if (marker.image_url) {
      popupContent += `<div style="margin-bottom: 8px;">
        <img src="${marker.image_url}" 
          style="width: 100%; max-height: 150px; object-fit: cover; border-radius: 4px; display: block;" 
          alt="${marker.location_name}"
          onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
        <div style="display: none; padding: 20px; background: #f0f0f0; text-align: center; border-radius: 4px;">
          📷 Imagen no disponible
        </div>
      </div>`;
    }
    
    if (marker.description) {
      popupContent += `<p style="margin: 0 0 8px 0; font-size: 0.9em; color: #555;">${marker.description}</p>`;
    }
    
    popupContent += `<p style="margin: 0; font-size: 0.75em; color: #999;">
      📅 ${new Date(marker.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })}
    </p></div>`;

    leafletMarker.bindPopup(popupContent, {
      maxWidth: 300,
      className: 'custom-popup'
    });

    leafletMarker.on('click', () => {
      selectedMarker.value = marker;
      emit('markerClick', marker);
    });

    markerLayers.set(marker.id, leafletMarker);
  });

  // Ajustar vista para mostrar todos los marcadores
  if (props.markers.length > 0) {
    const bounds = L.latLngBounds(
      props.markers.map(m => [m.latitude, m.longitude])
    );
    map!.fitBounds(bounds, { padding: [50, 50] });
  }
}

onMounted(() => {
  initMap();
});

watch(() => props.markers, () => {
  updateMarkers();
  // Forzar recalcular tamaño cuando cambien los marcadores
  setTimeout(() => {
    if (map) {
      map.invalidateSize();
    }
  }, 100);
}, { deep: true });

onBeforeUnmount(() => {
  if (map) {
    map.remove();
    map = null;
  }
});
</script>

<style scoped>
.map-viewer {
  position: relative;
  width: 100%;
  height: 100%;
}

.map {
  width: 100%;
  height: 100%;
  z-index: 0;
}

.marker-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-width: 400px;
  overflow: hidden;
}

.marker-info-content {
  padding: 1rem;
}

.marker-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--ion-color-primary);
}

.description {
  color: var(--ion-color-dark);
  margin: 0.5rem 0;
}

.coordinates,
.date {
  font-size: 0.875rem;
  color: var(--ion-color-medium);
  margin: 0.25rem 0;
}

.marker-info img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
</style>
