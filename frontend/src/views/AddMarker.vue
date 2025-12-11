<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/my-map"></ion-back-button>
        </ion-buttons>
        <ion-title>Añadir Lugar</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <form @submit.prevent="handleSubmit">
        <ion-list>
          <ion-item>
            <ion-input
              label="País o Ciudad"
              label-placement="floating"
              v-model="formData.location_name"
              placeholder="Ej: Paris, France"
              required
            ></ion-input>
          </ion-item>

          <ion-item>
            <ion-textarea
              label="Descripción (opcional)"
              label-placement="floating"
              v-model="formData.description"
              placeholder="Cuéntanos sobre tu visita..."
              :rows="4"
            ></ion-textarea>
          </ion-item>

          <ion-item>
            <ion-label position="stacked">Foto del lugar (opcional)</ion-label>
            <input
              type="file"
              accept="image/*"
              @change="handleImageSelect"
              ref="fileInput"
              style="margin-top: 10px;"
            />
          </ion-item>

          <!-- Vista previa de la imagen -->
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Vista previa" />
            <ion-button size="small" fill="clear" color="danger" @click="removeImage">
              Eliminar foto
            </ion-button>
          </div>
        </ion-list>

        <div class="button-container">
          <ion-button
            expand="block"
            type="submit"
            :disabled="!formData.location_name || loading"
          >
            <ion-spinner v-if="loading" name="crescent"></ion-spinner>
            <span v-else>Añadir Marcador</span>
          </ion-button>
        </div>

        <ion-text v-if="error" color="danger" class="error-text">
          <p>{{ error }}</p>
        </ion-text>
      </form>
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
  IonList,
  IonItem,
  IonInput,
  IonTextarea,
  IonLabel,
  IonButton,
  IonButtons,
  IonBackButton,
  IonSpinner,
  IonText,
  toastController,
} from '@ionic/vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useMarkerStore } from '@/stores/marker';
import type { MarkerCreate } from '@/interfaces/mimapa';

const router = useRouter();
const markerStore = useMarkerStore();

const formData = ref<MarkerCreate>({
  location_name: '',
  description: '',
});

const imageFile = ref<File | null>(null);
const imagePreview = ref<string | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

function handleImageSelect(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];

  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

function removeImage() {
  imageFile.value = null;
  imagePreview.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function handleSubmit() {
  if (!formData.value.location_name) {
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    await markerStore.createMarker(formData.value, imageFile.value || undefined);

    const toast = await toastController.create({
      message: '¡Marcador añadido correctamente!',
      duration: 2000,
      color: 'success',
      position: 'top',
    });
    await toast.present();

    // Forzar recarga de marcadores antes de navegar
    await markerStore.loadMyMarkers(true);
    
    router.push('/my-map');
  } catch (err: any) {
    error.value = err.message || 'Error al añadir marcador';

    const toast = await toastController.create({
      message: error.value,
      duration: 3000,
      color: 'danger',
      position: 'top',
    });
    await toast.present();
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.button-container {
  margin-top: 2rem;
}

.image-preview {
  padding: 1rem;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.error-text {
  display: block;
  margin-top: 1rem;
  text-align: center;
}
</style>
