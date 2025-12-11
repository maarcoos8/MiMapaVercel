# Backend Dockerfile para MiMapa
FROM python:3.12-slim

WORKDIR /app

# Copiar requirements primero para aprovechar el caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/

# Exponer el puerto
EXPOSE 8000

# El comando se define en docker-compose.yml para permitir --reload

