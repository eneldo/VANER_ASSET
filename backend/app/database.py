# =========================================================
# DATABASE CONFIGURATION
# Archivo: app/database.py
# Configuración SQLAlchemy Profesional
# Compatible con Alembic + PostgreSQL
# =========================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings


# =========================================================
# ENGINE PRINCIPAL
# =========================================================
# pool_pre_ping:
# Verifica conexiones muertas automáticamente
#
# pool_recycle:
# Evita desconexiones por timeout
#
# echo:
# Mostrar SQL en consola (solo desarrollo)
# =========================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)


# =========================================================
# SESSION LOCAL
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================================================
# BASE GLOBAL MODELOS
# =========================================================

Base = declarative_base()


# =========================================================
# DEPENDENCIA FASTAPI
# =========================================================

def get_db():
    """
    Genera una sesión de base de datos
    para cada request y la cierra automáticamente.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()