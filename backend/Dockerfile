# =========================================================
# BACKEND SGAHolding
# Dockerfile Producción
# =========================================================

ARG PYTHON_IMAGE=python:3.12.11-slim-bookworm
FROM ${PYTHON_IMAGE}

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

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
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

COPY alembic.ini entrypoint.sh ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts

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
