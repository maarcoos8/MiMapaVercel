# Usar una imagen ligera de Node
FROM node:18-alpine

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar archivos de dependencias primero para aprovechar el caché de Docker
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer el puerto de Vite
EXPOSE 5173

# Comando para desarrollo (host 0.0.0.0 es necesario para que sea accesible desde fuera del contenedor)
CMD ["npm", "run", "dev", "--", "--host"]