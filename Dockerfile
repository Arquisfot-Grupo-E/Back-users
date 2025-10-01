# Usar una versión específica de Python para la reproducibilidad
FROM python:3.12-slim

# Establecer variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar las dependencias del sistema necesarias para psycopg2 y postgresql-client
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client && rm -rf /var/lib/apt/lists/*

# Copiar solo el archivo de requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# El código de la aplicación se montará como un volumen desde docker-compose.
# NO lo copiamos aquí para permitir el hot-reloading.