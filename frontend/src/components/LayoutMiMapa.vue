<template>
  <ion-page>
    <ion-header :translucent="true">
      <ion-toolbar>
        <div slot="start" class="logo-container" @click="goToHome">
          <ion-icon :icon="mapOutline" class="logo-icon"></ion-icon>
          <span class="logo-title">MiMapa</span>
        </div>
        
        <ion-buttons slot="start" v-if="showBackButton">
          <ion-back-button default-href="/my-map"></ion-back-button>
        </ion-buttons>

        <ion-buttons slot="end" v-if="isAuthenticated">
          <ion-button @click="goToVisitMap">
            <ion-icon :icon="searchOutline"></ion-icon>
          </ion-button>
          <ion-button @click="openProfilePopover($event)">
            <ion-icon :icon="personCircleOutline"></ion-icon>
          </ion-button>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="false">
      <slot></slot>
    </ion-content>

    <!-- Popover de perfil -->
    <ion-popover
      :is-open="isProfilePopoverOpen"
      @didDismiss="isProfilePopoverOpen = false"
      :event="profileEvent"
      side="bottom"
      alignment="end"
    >
      <ion-content>
        <div class="profile-header">
          <div class="ion-padding">
            <h5 class="ion-no-margin">{{ user?.name || 'Usuario' }}</h5>
            <span class="email-text">{{ user?.email }}</span>
          </div>
        </div>
        <ion-list>
          <ion-item button @click="openThemePopover($event)">
            <ion-icon :icon="invertModeOutline" slot="start"></ion-icon>
            <ion-text>Tema</ion-text>
          </ion-item>
          <ion-item lines="none" button @click="handleLogout">
            <ion-icon :icon="logOutOutline" color="danger" slot="start"></ion-icon>
            <ion-text color="danger">Cerrar sesión</ion-text>
          </ion-item>
        </ion-list>
      </ion-content>
    </ion-popover>

    <!-- Popover de tema -->
    <ion-popover
      :is-open="isThemePopoverOpen"
      @didDismiss="isThemePopoverOpen = false"
      :event="themeEvent"
      side="start"
      alignment="center"
    >
      <ion-content>
        <ion-list>
          <ion-item
            v-for="option in themeOptions"
            :key="option.value"
            button
            @click="changeTheme(option.value)"
          >
            {{ option.label }}
            <ion-icon
              :icon="checkmarkOutline"
              slot="end"
              v-if="option.value === currentTheme"
            ></ion-icon>
          </ion-item>
        </ion-list>
      </ion-content>
    </ion-popover>
  </ion-page>
</template>

<script setup lang="ts">
import {
  IonContent,
  IonHeader,
  IonPage,
  IonButtons,
  IonButton,
  IonIcon,
  IonToolbar,
  IonPopover,
  IonList,
  IonItem,
  IonText,
  IonBackButton,
} from '@ionic/vue';
import {
  mapOutline,
  personCircleOutline,
  logOutOutline,
  invertModeOutline,
  checkmarkOutline,
  searchOutline,
} from 'ionicons/icons';
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import ThemeService from '@/services/shared/theme.service';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isProfilePopoverOpen = ref(false);
const isThemePopoverOpen = ref(false);
const profileEvent = ref<Event>();
const themeEvent = ref<Event>();
const currentTheme = ref(ThemeService.getTheme());

const user = computed(() => authStore.user);
const isAuthenticated = computed(() => authStore.isAuthenticated);
const showBackButton = computed(() => route.path !== '/my-map' && route.path !== '/login');

const themeOptions = [
  { label: 'Claro', value: 'light' },
  { label: 'Oscuro', value: 'dark' },
  { label: 'Sistema', value: 'auto' },
];

function goToHome() {
  if (isAuthenticated.value) {
    router.push('/my-map');
  } else {
    router.push('/login');
  }
}

function goToVisitMap() {
  router.push('/visit-map');
}

function openProfilePopover(event: Event) {
  profileEvent.value = event;
  isProfilePopoverOpen.value = true;
}

function openThemePopover(event: Event) {
  themeEvent.value = event;
  isThemePopoverOpen.value = true;
  isProfilePopoverOpen.value = false;
}

function changeTheme(theme: 'light' | 'dark' | 'system') {
  ThemeService.setTheme(theme);
  currentTheme.value = theme;
}

async function handleLogout() {
  isProfilePopoverOpen.value = false;
  await authStore.logout();
  router.push('/login');
}
</script>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0 1rem;
}

.logo-icon {
  font-size: 28px;
  color: var(--ion-color-primary);
}

.logo-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ion-color-primary);
}

.profile-header {
  border-bottom: 1px solid var(--ion-color-light);
}

.email-text {
  color: var(--ion-color-medium);
  font-size: 0.875rem;
}

ion-item {
  --padding-start: 16px;
  --inner-padding-end: 16px;
}
</style>
