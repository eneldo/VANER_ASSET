# =========================================================
# BACKEND SGAHolding
# Dockerfile Producción
# =========================================================

FROM python:3.12-slim

# =========================================================
# VARIABLES
# =========================================================

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================================================
# DIRECTORIO
# =========================================================

WORKDIR /app

# =========================================================
# DEPENDENCIAS SISTEMA
# =========================================================

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    qpdf \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# INSTALAR DEPENDENCIAS PYTHON
# =========================================================

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# =========================================================
# COPIAR PROYECTO
# =========================================================

COPY . .

# =========================================================
# CREAR CARPETAS
# =========================================================

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/uploads/evidencias /app/backups/postgres /app/exports \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app

# =========================================================
# PUERTO
# =========================================================

EXPOSE 8000

# =========================================================
# COMANDO INICIO
# =========================================================

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
