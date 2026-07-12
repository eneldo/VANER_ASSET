# ============================================================
# ALEMBIC ENV - SGA SAAS PRO
# Archivo: backend/alembic/env.py
# Migraciones profesionales con SQLAlchemy + PostgreSQL
# ============================================================

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# ============================================================
# IMPORTAR CONFIGURACIÓN DEL PROYECTO
# ============================================================

from app.config import settings
from app.database import Base

# ============================================================
# IMPORTAR TODOS LOS MODELOS
# IMPORTANTE:
# Alembic necesita cargar estos archivos para detectar
# tablas, columnas, llaves foráneas y cambios futuros.
# ============================================================

import app.models.usuario
import app.models.empresa
import app.models.sede
import app.models.categoria
import app.models.equipo
import app.models.equipo_hoja_vida
import app.models.evidencia
import app.models.formato_dinamico
import app.models.formato_mantenimiento
import app.models.hist_mantenimiento
import app.models.historial_mantenimiento
import app.models.login_attempt
import app.models.mantenimiento
import app.models.notificacion
import app.models.password_reset
import app.models.permiso
import app.models.refresh_token
import app.models.security_event
import app.models.tecnico
import app.models.auditoria
import app.models.auditoria_evento
import app.models.auditoria_pro
import app.models.solicitud_correctiva
import app.models.reporte_publicado
import app.models.factura
import app.models.ot_repuesto
import app.models.ot_incidencia
import app.models.plantilla_reporte
import app.models.automatizacion
import app.models.backup_historial
import app.models.configuracion
import app.models.configuracion_saas
import app.models.devops_evento
import app.models.log_sistema
import app.models.monitor_estado
import app.models.scheduler_inteligente
import app.models.smtp_log

# ============================================================
# CONFIGURACIÓN BASE DE ALEMBIC
# ============================================================

config = context.config

# Usar la DATABASE_URL real del archivo .env
config.set_main_option(
    "sqlalchemy.url",
    settings.MIGRATION_DATABASE_URL or settings.DATABASE_URL,
)

# Logging de Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata global de SQLAlchemy
target_metadata = Base.metadata


# ============================================================
# MIGRACIONES OFFLINE
# ============================================================

def run_migrations_offline() -> None:
    """
    Ejecuta migraciones sin conexión directa al motor.
    Se usa principalmente para generar SQL.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# MIGRACIONES ONLINE
# ============================================================

def run_migrations_online() -> None:
    """
    Ejecuta migraciones conectándose directamente a PostgreSQL.
    Este será el modo usado normalmente.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# EJECUTAR SEGÚN MODO
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
