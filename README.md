# MiMapa - Docker Setup

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno
```bash
cp .env.example .env
```

Edita el archivo `.env` y completa:
- `GOOGLE_CLIENT_ID`: ID de tu aplicación OAuth de Google
- `GOOGLE_CLIENT_SECRET`: Secret de tu aplicación OAuth de Google

### 2. Levantar los servicios
```bash
docker-compose up -d
```

Esto iniciará:
- **MongoDB** en `localhost:27017` (usuario: `admin`, password: `password123`)
- **Backend** en `http://localhost:8000`
- **Frontend** en `http://localhost:5173`

### 3. Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### 4. Detener los servicios
```bash
docker-compose down
```

## 🔧 Comandos útiles

```bash
# Reconstruir imágenes
docker-compose build

# Reconstruir y levantar
docker-compose up --build

# Eliminar volúmenes (borra la base de datos)
docker-compose down -v

# Ejecutar comando en el backend
docker-compose exec backend bash

# Ejecutar comando en MongoDB
docker-compose exec mongodb mongosh -u admin -p password123
```

## 📦 Estructura

```
├── docker-compose.yml          # Orquestación de servicios
├── .env.example               # Plantilla de variables de entorno
├── backend/
│   ├── Dockerfile             # Imagen de FastAPI
│   └── app/                   # Código del backend (montado como volumen)
└── frontend/
    ├── Dockerfile             # Imagen de Node/Vite
    └── src/                   # Código del frontend (montado como volumen)
```

## 🔑 OAuth Google Setup

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google+
4. Ve a "Credenciales" → "Crear credenciales" → "ID de cliente de OAuth 2.0"
5. Configura las URIs autorizadas:
   - **Orígenes autorizados**: `http://localhost:5173`, `http://localhost:8000`
   - **URIs de redirección**: `http://localhost:8000/auth/callback/google`
6. Copia el Client ID y Client Secret al archivo `.env`
