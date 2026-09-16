# ============================================================
# VANER ASSET - Backend
# Dockerfile de Producción
# Actualizado: 2026
# ============================================================

ARG PYTHON_IMAGE=python:3.12.14-slim-bookworm
FROM ${PYTHON_IMAGE}

# ============================================================
# VARIABLES DE ENTORNO
# ============================================================

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# ============================================================
# DIRECTORIO DE TRABAJO
# ============================================================

WORKDIR /app

# ============================================================
# DEPENDENCIAS DEL SISTEMA
# ============================================================

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client-16 \
        qpdf \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# DEPENDENCIAS PYTHON
# ============================================================

COPY requirements.txt ./

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# ============================================================
# CÓDIGO DE LA APLICACIÓN
# ============================================================

COPY alembic.ini entrypoint.sh ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts

# ============================================================
# USUARIO NO ROOT Y DIRECTORIOS PERSISTENTES
# ============================================================

RUN useradd \
        --create-home \
        --uid 10001 \
        --shell /usr/sbin/nologin \
        appuser \
    && mkdir -p \
        /app/uploads/evidencias \
        /app/backups/postgres \
        /app/exports \
    && chmod 0755 /app/entrypoint.sh \
    && chown -R appuser:appuser /app

# ============================================================
# PUERTO
# ============================================================

EXPOSE 8000

# ============================================================
# EJECUCIÓN
# ============================================================

USER appuser

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]

