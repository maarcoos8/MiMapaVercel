from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import logging
from app.database.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, markers, visits
from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Variable global para almacenar el cliente de MongoDB
mongo_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    mongo_client = await connect_to_mongo()
    yield
    await close_mongo_connection(mongo_client)

app = FastAPI(
    title="MiMapa API",
    description="API para la aplicación MiMapa - Gestión de mapas personales con marcadores",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar SessionMiddleware (requerido para OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY
)

# Configurar CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(markers.router)
app.include_router(visits.router)

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "service": "MiMapa API", 
        "version": "1.0.0",
        "description": "API para gestión de mapas personales con OAuth 2.0, geocoding e imágenes"
    }