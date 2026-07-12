# =========================================================
# CONFIGURACIÓN GENERAL SGA PRO
# Archivo: app/config.py
# Compatible con Pydantic v2 + Alembic + Producción
# =========================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =====================================================
    # INFORMACIÓN GENERAL
    # =====================================================

    APP_NAME: str = "SGA PRO"
    APP_ENV: str = "development"

    # development / production
    DEBUG: bool = False

    # =====================================================
    # SERVIDOR
    # =====================================================

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # =====================================================
    # BASE DE DATOS
    # =====================================================

    DATABASE_URL: str

    # Debe apuntar a un rol propietario/DDL y usarse solo desde Alembic.
    # La aplicación web debe conectarse con DATABASE_URL y un rol sin BYPASSRLS.
    MIGRATION_DATABASE_URL: str | None = None

    # =====================================================
    # SEGURIDAD JWT
    # =====================================================

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # =====================================================
    # UPLOADS / ARCHIVOS
    # =====================================================

    UPLOAD_DIR: str = "app/uploads"

    # =====================================================
    # EXPORTACIONES
    # =====================================================

    EXPORT_DIR: str = "app/exports"

    # =====================================================
    # CORS
    # =====================================================

    BACKEND_CORS_ORIGINS: str = "*"

    # =====================================================
    # CONFIGURACIÓN PYDANTIC
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        extra="ignore",
        case_sensitive=True
    )


# =========================================================
# INSTANCIA GLOBAL
# =========================================================

settings = Settings()
