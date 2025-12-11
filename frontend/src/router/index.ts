import { createRouter, createWebHistory } from '@ionic/vue-router';
import { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: 'Iniciar Sesión - MiMapa'
    }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('@/views/AuthCallback.vue'),
    meta: {
      title: 'Autenticando...'
    }
  },
  {
    path: '/my-map',
    name: 'MyMap',
    component: () => import('@/views/MyMap.vue'),
    meta: {
      title: 'Mi Mapa - MiMapa',
      requiresAuth: true
    }
  },
  {
    path: '/add-marker',
    name: 'AddMarker',
    component: () => import('@/views/AddMarker.vue'),
    meta: {
      title: 'Añadir Lugar - MiMapa',
      requiresAuth: true
    }
  },
  {
    path: '/visit-map',
    name: 'VisitMap',
    component: () => import('@/views/VisitMap.vue'),
    meta: {
      title: 'Visitar Mapa - MiMapa',
      requiresAuth: true
    }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Navigation guard para rutas protegidas
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token');
  
  // Rutas públicas que no requieren autenticación
  const publicRoutes = ['/login', '/auth/callback'];
  const isPublicRoute = publicRoutes.includes(to.path);

  if (!isPublicRoute && !token) {
    // Si no es una ruta pública y no hay token, redirigir a login
    next('/login');
  } else if (to.path === '/login' && token) {
    // Si ya está autenticado e intenta ir a login, redirigir a my-map
    next('/my-map');
  } else {
    next();
  }
});

export default router;