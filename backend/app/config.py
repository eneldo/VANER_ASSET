# =========================================================
# CONFIGURACIÓN GENERAL SGAHolding
# Archivo: app/config.py
# Compatible con Pydantic v2 + Alembic + Producción
# =========================================================

from base64 import urlsafe_b64decode

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):

    # =====================================================
    # INFORMACIÓN GENERAL
    # =====================================================

    APP_NAME: str = "SGAHolding"
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
    BACKUP_DATABASE_URL: str | None = None

    # =====================================================
    # SEGURIDAD JWT
    # =====================================================

    SECRET_KEY: str

    CONFIG_ENCRYPTION_KEY: str | None = None
    BOOTSTRAP_ADMIN_TOKEN: str | None = None

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REFRESH_COOKIE_NAME: str = 'sga_refresh_token'
    REFRESH_COOKIE_PATH: str = '/auth'
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = 'lax'
    FRONTEND_URL: str = "http://localhost:5173"
    RUN_MIGRATIONS: bool = False
    RUN_SCHEDULER: bool = True
    ALLOW_DATABASE_RESTORE: bool = False

    REDIS_URL: str | None = None
    RATE_LIMIT_REDIS_REQUIRED: bool = False
    BACKUP_ENCRYPTION_REQUIRED: bool = False

    S3_BACKUP_ENABLED: bool = False
    S3_BACKUP_ENDPOINT_URL: str | None = None
    S3_BACKUP_REGION: str = "auto"
    S3_BACKUP_BUCKET: str | None = None
    S3_BACKUP_ACCESS_KEY_ID: str | None = None
    S3_BACKUP_SECRET_ACCESS_KEY: str | None = None
    S3_BACKUP_PREFIX: str = "sga-production"

    # =====================================================
    # UPLOADS / ARCHIVOS
    # =====================================================

    UPLOAD_DIR: str = "app/uploads"
    BACKUP_DIR: str = "app/backups"
    MAX_INVENTORY_IMPORT_MB: int = 10
    MAX_INVENTORY_IMPORT_ROWS: int = 10000

    # =====================================================
    # EXPORTACIONES
    # =====================================================

    EXPORT_DIR: str = "app/exports"

    # =====================================================
    # CORS
    # =====================================================

    BACKEND_CORS_ORIGINS: str = "*"

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.APP_ENV.lower() != "production":
            return self

        if self.DEBUG:
            raise ValueError("DEBUG must be disabled in production")
        if len(self.SECRET_KEY) < 32 or any(
            marker in self.SECRET_KEY.upper() for marker in ("CAMBIAR", "CHANGE_ME")
        ):
            raise ValueError("SECRET_KEY must be random and at least 32 characters")
        if not self.REFRESH_COOKIE_SECURE:
            raise ValueError("REFRESH_COOKIE_SECURE must be true in production")
        if not self.FRONTEND_URL.startswith("https://"):
            raise ValueError("FRONTEND_URL must use HTTPS in production")
        if self.ACCESS_TOKEN_EXPIRE_MINUTES > 60:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES cannot exceed 60 in production")
        if not self.CONFIG_ENCRYPTION_KEY:
            raise ValueError("CONFIG_ENCRYPTION_KEY is required in production")
        if not self.BACKUP_DATABASE_URL:
            raise ValueError("BACKUP_DATABASE_URL is required in production")
        if self.RATE_LIMIT_REDIS_REQUIRED and not self.REDIS_URL:
            raise ValueError("REDIS_URL is required when distributed rate limiting is enabled")
        if self.BACKUP_ENCRYPTION_REQUIRED and not self.CONFIG_ENCRYPTION_KEY:
            raise ValueError("CONFIG_ENCRYPTION_KEY is required to encrypt backups")

        try:
            app_database = make_url(self.DATABASE_URL)
            backup_database = make_url(self.BACKUP_DATABASE_URL)
        except Exception as exc:
            raise ValueError("Database URLs must be valid") from exc
        if not backup_database.username:
            raise ValueError("BACKUP_DATABASE_URL must include a username")
        if backup_database.username == app_database.username:
            raise ValueError("BACKUP_DATABASE_URL must use a dedicated backup role")
        if backup_database.username != "sga_backup":
            raise ValueError("BACKUP_DATABASE_URL must use the sga_backup role")

        try:
            decoded_key = urlsafe_b64decode(self.CONFIG_ENCRYPTION_KEY.encode("ascii"))
        except Exception as exc:
            raise ValueError("CONFIG_ENCRYPTION_KEY must be a valid Fernet key") from exc
        if len(decoded_key) != 32:
            raise ValueError("CONFIG_ENCRYPTION_KEY must be a valid Fernet key")

        if self.S3_BACKUP_ENABLED and not all(
            (
                self.S3_BACKUP_ENDPOINT_URL,
                self.S3_BACKUP_BUCKET,
                self.S3_BACKUP_ACCESS_KEY_ID,
                self.S3_BACKUP_SECRET_ACCESS_KEY,
            )
        ):
            raise ValueError("All S3_BACKUP_* credentials are required when backups are enabled")

        return self

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
