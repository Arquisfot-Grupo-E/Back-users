# --- Etapa de construcción (Builder Stage) ---
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependencias del sistema operativo necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copiar solo el archivo de requerimientos para aprovechar el cache de Docker
COPY requirements.txt .

# Crear un entorno virtual dentro de la imagen
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar las dependencias de Python en el entorno virtual
RUN pip install --no-cache-dir -r requirements.txt


# --- Etapa final (Final Stage) ---
FROM python:3.12-slim

WORKDIR /app

# --- LÍNEA AÑADIDA ---
# Instalar solo las librerías cliente de PostgreSQL necesarias en tiempo de ejecución
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual con las dependencias ya instaladas desde la etapa 'builder'
COPY --from=builder /opt/venv /opt/venv

# Copiar el código de la aplicación
COPY . .

# Activar el entorno virtual para los comandos subsiguientes
ENV PATH="/opt/venv/bin:$PATH"

# Exponer el puerto que Django usará dentro del contenedor
EXPOSE 8001