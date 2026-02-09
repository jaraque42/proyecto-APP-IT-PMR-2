FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos dependencias del sistema mínimas (si alguna dependencia necesita compilarse)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiamos solo requirements primero para aprovechar la cache de Docker
COPY requirements.txt ./

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt gunicorn

# Copiamos el resto del proyecto
COPY . .

# Aseguramos que existan las rutas que la app usa para persistencia
RUN mkdir -p /app/pdfs \
    && touch /app/entregas.db || true

EXPOSE 5000

VOLUME ["/app/pdfs", "/app/entregas.db"]

# Usamos gunicorn para producción (usa la app definida en app:app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
