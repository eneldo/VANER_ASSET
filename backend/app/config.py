# =========================================================
# CONFIGURACIÓN GENERAL SGA PRO (VERSIÓN CORREGIDA)
# Compatible con Pydantic v2
# =========================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =====================================================
    # DATOS GENERALES
    # =====================================================

    APP_NAME: str = "SGA PRO"
    APP_ENV: str = "development"

    # IMPORTANTE: ahora sí se reconoce DEBUG
    DEBUG: bool = False

    # =====================================================
    # BASE DE DATOS
    # =====================================================

    DATABASE_URL: str

    # =====================================================
    # SEGURIDAD
    # =====================================================

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # =====================================================
    # ARCHIVOS / UPLOADS
    # =====================================================

    # IMPORTANTE: ahora sí se reconoce UPLOAD_DIR
    UPLOAD_DIR: str = "app/uploads"

    # =====================================================
    # CONFIGURACIÓN Pydantic
    # 👇 CLAVE DE LA SOLUCIÓN
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # 🔥 evita que falle por variables extra
    )


# Instancia global
settings = Settings()