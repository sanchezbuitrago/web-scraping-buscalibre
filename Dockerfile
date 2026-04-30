FROM python:3.11-slim

# Instalamos dependencias del sistema necesarias para Selenium/Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN ls
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Por defecto no definimos CMD, lo definiremos en docker-compose