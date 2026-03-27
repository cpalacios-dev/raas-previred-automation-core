# Imagen base de Python (usar versión compatible con Cloud Run)
FROM python:3.12-slim

# Variables de entorno
ARG PORT=8080
ENV PORT=$PORT \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias básicas del sistema
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium con TODAS sus dependencias del sistema
# --with-deps instala automáticamente librerías necesarias (libnss3, libgbm, etc.)
RUN playwright install --with-deps chromium

# Copiar el código de la aplicación
COPY . .

# Crear directorio para logs y datos
RUN mkdir -p /app/app/logs /app/app/data/debug /app/app/data/input /app/app/data/output

# Exponer puerto
EXPOSE 8080

# Comando de inicio (ajustar según tu punto de entrada)
# Para Cloud Run con Flask API:
CMD ["python", "app/app.py"]

# Si se ejecuta como proceso directo (main.py), descomentar:
# CMD ["python", "app/main.py"]
 