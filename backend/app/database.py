# =========================================================
# CONEXIÓN A POSTGRESQL CON SQLALCHEMY
# =========================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


# Motor de conexión a PostgreSQL
engine = create_engine(settings.DATABASE_URL)


# Sesión para operaciones con la base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base para todos los modelos
Base = declarative_base()


def get_db():
    """
    Abre una sesión de base de datos para cada petición
    y la cierra automáticamente al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()