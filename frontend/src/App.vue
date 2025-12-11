<template>
  <ion-app>
    <ion-router-outlet />
  </ion-app>
</template>

<script setup lang="ts">
import { IonApp, IonRouterOutlet } from '@ionic/vue';

import ThemeService from '@/services/shared/theme.service';
ThemeService.initializeTheme();

</script>
