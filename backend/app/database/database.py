import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.marker import Marker
from app.models.visit import Visit


async def connect_to_mongo():
    logging.info("Conectando a MongoDB...")
    client = AsyncIOMotorClient(settings.MONGODB_CONNECTION_STRING)
    
    await init_beanie(
        database=client[settings.MONGODB_DATABASE_NAME],
        document_models=[User, Marker, Visit]
    )
    
    logging.info("Conexión a MongoDB y Beanie inicializados exitosamente.")
    return client

async def close_mongo_connection(client: AsyncIOMotorClient):
    logging.info("Cerrando conexión a MongoDB...")
    client.close()
    logging.info("Conexión a MongoDB cerrada.")