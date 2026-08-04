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

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REFRESH_COOKIE_NAME: str = 'sga_refresh_token'
    REFRESH_COOKIE_PATH: str = '/auth'
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = 'lax'
    RUN_SCHEDULER: bool = True

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
