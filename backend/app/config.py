# =========================================================
# CONFIGURACIÓN GENERAL VANER ASSET
# Archivo: app/config.py
# Compatible con Pydantic v2 + Alembic + Producción
# =========================================================

from base64 import urlsafe_b64decode
import re

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from app.product import PRODUCT_NAME


class Settings(BaseSettings):

    # =====================================================
    # INFORMACIÓN GENERAL
    # =====================================================

    APP_NAME: str = PRODUCT_NAME
    CLIENT_CODE: str = "local"
    CLIENT_NAME: str = "Entorno local"
    APP_DOMAIN: str = "localhost"
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

    REFRESH_COOKIE_NAME: str = 'vaner_asset_refresh_token'
    REFRESH_COOKIE_PATH: str = '/auth'
    REFRESH_COOKIE_SECURE: bool = False
    REFRESH_COOKIE_SAMESITE: str = 'lax'
    FRONTEND_URL: str | None = None
    RUN_MIGRATIONS: bool = False
    RUN_SCHEDULER: bool = True
    ALLOW_DATABASE_RESTORE: bool = False

    REDIS_URL: str | None = None
    RATE_LIMIT_REDIS_REQUIRED: bool = False
    BACKUP_ENCRYPTION_REQUIRED: bool = False

    # =====================================================
    # POLÍTICA DE CONTRASEÑAS
    # =====================================================

    PASSWORD_MIN_LENGTH: int = 15
    PASSWORD_MIN_LENGTH_WITH_MFA: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_HISTORY_COUNT: int = 5
    TEMP_PASSWORD_EXPIRATION_HOURS: int = 24
    PASSWORD_RESET_EXPIRATION_MINUTES: int = 15
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4

    S3_BACKUP_ENABLED: bool = False
    S3_BACKUP_ENDPOINT_URL: str | None = None
    S3_BACKUP_REGION: str = "auto"
    S3_BACKUP_BUCKET: str | None = None
    S3_BACKUP_ACCESS_KEY_ID: str | None = None
    S3_BACKUP_SECRET_ACCESS_KEY: str | None = None
    S3_BACKUP_PREFIX: str = "vaner-asset-production"

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

    BACKEND_CORS_ORIGINS: str = ""

    @field_validator("CLIENT_CODE")
    @classmethod
    def validate_client_code(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,62}", normalized):
            raise ValueError(
                "CLIENT_CODE must contain 2-63 lowercase letters, numbers, underscores or hyphens"
            )
        return normalized

    @field_validator("APP_DOMAIN")
    @classmethod
    def validate_app_domain(cls, value: str) -> str:
        normalized = value.strip().lower().rstrip(".")
        if not normalized or "://" in normalized or "/" in normalized or " " in normalized:
            raise ValueError("APP_DOMAIN must be a hostname without scheme or path")
        return normalized

    @model_validator(mode="after")
    def validate_production_security(self):
        production = self.APP_ENV.lower() == "production"
        default_scheme = "https" if production else "http"
        if not self.FRONTEND_URL:
            self.FRONTEND_URL = (
                "http://localhost:5173"
                if not production and self.APP_DOMAIN == "localhost"
                else f"{default_scheme}://{self.APP_DOMAIN}"
            )
        self.FRONTEND_URL = self.FRONTEND_URL.rstrip("/")
        if not self.BACKEND_CORS_ORIGINS.strip():
            self.BACKEND_CORS_ORIGINS = self.FRONTEND_URL

        if not production:
            return self

        if self.CLIENT_CODE in {"local", "default"}:
            raise ValueError("CLIENT_CODE must identify the production deployment")
        if not self.CLIENT_NAME.strip():
            raise ValueError("CLIENT_NAME is required in production")
        if self.APP_DOMAIN in {"localhost", "127.0.0.1"}:
            raise ValueError("APP_DOMAIN must identify the production hostname")
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
        if backup_database.username != "vaner_backup":
            raise ValueError("BACKUP_DATABASE_URL must use the vaner_backup role")

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
    # SENTRY / OBSERVABILIDAD
    # =====================================================

    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% de traces
    SENTRY_ENVIRONMENT: str | None = None  # fallback a APP_ENV

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
