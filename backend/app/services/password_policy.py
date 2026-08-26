# =========================================================
# SERVICIO CENTRALIZADO DE POLÍTICA DE CONTRASEÑAS
# Archivo: backend/app/services/password_policy.py
#
# Valida contraseñas según políticas OWASP/NIST.
# Reutilizable desde: creación, cambio, recuperación, admin.
# =========================================================

import re
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.usuario import Usuario


# =========================================================
# LISTA LOCAL DE TÉRMINOS PROHIBIDOS
# =========================================================

COMMON_PASSWORDS = frozenset({
    "password", "contraseña", "contrasena", "admin", "administrador",
    "admin123", "123456", "12345678", "qwerty", "vaner", "vanerasset",
    "vaner asset", "inventario", "mantenimiento", "empresa123",
    "letmein", "welcome", "monkey", "dragon", "master", "login",
    "abc123", "111111", "1234567", "123456789", "1234567890",
    "iloveyou", "trustno1", "sunshine", "princess", "football",
    "shadow", "superman", "michael", "ninja", "mustang", "password1",
    "passwordpassword", "password123", "admin12345", "qwerty123",
})

VANER_TERMS = frozenset({
    "vaner", "vanerasset", "vaner asset", "vaner software",
    "inventario", "mantenimiento", "activos", "equipos",
})


# =========================================================
# CÓDIGOS DE ERROR ESTRUCTURADOS
# =========================================================

class PasswordErrorCode:
    TOO_SHORT = "PASSWORD_TOO_SHORT"
    TOO_LONG = "PASSWORD_TOO_LONG"
    COMMON = "PASSWORD_COMMON"
    COMPROMISED = "PASSWORD_COMPROMISED"
    CONTAINS_USERNAME = "PASSWORD_CONTAINS_USERNAME"
    CONTAINS_EMAIL = "PASSWORD_CONTAINS_EMAIL"
    CONTAINS_TENANT_DATA = "PASSWORD_CONTAINS_TENANT_DATA"
    RECENTLY_USED = "PASSWORD_RECENTLY_USED"
    SAME_AS_CURRENT = "PASSWORD_SAME_AS_CURRENT"


# =========================================================
# RESULTADO DE VALIDACIÓN
# =========================================================

@dataclass
class PasswordValidationResult:
    valid: bool = True
    errors: list = field(default_factory=list)
    codes: list = field(default_factory=list)

    def reject(self, code: str, message: str):
        self.valid = False
        self.errors.append(message)
        self.codes.append(code)


# =========================================================
# CONFIGURACIÓN DE POLÍTICA
# =========================================================

def _cfg(key: str, default):
    return getattr(settings, key, default) or default


def get_password_policy():
    """Retorna la política de contraseñas vigente."""
    return {
        "min_length": int(_cfg("PASSWORD_MIN_LENGTH", 15)),
        "min_length_mfa": int(_cfg("PASSWORD_MIN_LENGTH_WITH_MFA", 12)),
        "max_length": int(_cfg("PASSWORD_MAX_LENGTH", 128)),
        "history_count": int(_cfg("PASSWORD_HISTORY_COUNT", 5)),
        "temp_password_hours": int(_cfg("TEMP_PASSWORD_EXPIRATION_HOURS", 24)),
        "reset_token_minutes": int(_cfg("PASSWORD_RESET_EXPIRATION_MINUTES", 15)),
    }


# =========================================================
# SERVICIO DE VALIDACIÓN CENTRALIZADO
# =========================================================

class PasswordPolicyService:
    """Servicio centralizado y reutilizable para validar contraseñas."""

    def __init__(self, policy: Optional[dict] = None):
        self.policy = policy or get_password_policy()

    def validate(
        self,
        password: str,
        *,
        usuario: Optional[Usuario] = None,
        db: Optional[Session] = None,
        is_temporary: bool = False,
    ) -> PasswordValidationResult:
        """
        Valida una contraseña contra la política completa.

        Args:
            password: Contraseña a validar.
            usuario: Usuario propietario (para detectar datos personales).
            db: Sesión de BD (para verificar historial).
            is_temporary: Si es True, aplica longitud mínima con MFA.

        Returns:
            PasswordValidationResult con valid/errors/codes.
        """
        result = PasswordValidationResult()

        if not isinstance(password, str):
            result.reject(PasswordErrorCode.TOO_SHORT, "La contraseña debe ser una cadena de texto.")
            return result

        min_len = self.policy["min_length_mfa"] if is_temporary else self.policy["min_length"]
        max_len = self.policy["max_length"]

        if len(password) < min_len:
            result.reject(
                PasswordErrorCode.TOO_SHORT,
                f"La contraseña debe tener al menos {min_len} caracteres.",
            )

        if len(password) > max_len:
            result.reject(
                PasswordErrorCode.TOO_LONG,
                f"La contraseña no debe exceder {max_len} caracteres.",
            )

        if not result.valid:
            return result

        self._check_common(password, result)
        self._check_vaner_terms(password, result)

        if usuario:
            self._check_personal_data(password, usuario, result)

        if db and usuario:
            self._check_history(password, usuario, db, result)

        return result

    def validate_change(
        self,
        new_password: str,
        current_password: str,
        *,
        usuario: Usuario,
        db: Session,
    ) -> PasswordValidationResult:
        """Valida cambio de contraseña desde sesión autenticada."""
        result = self.validate(new_password, usuario=usuario, db=db)

        if current_password and new_password == current_password:
            result.reject(
                PasswordErrorCode.SAME_AS_CURRENT,
                "La nueva contraseña no puede ser igual a la actual.",
            )

        return result

    def _check_common(self, password: str, result: PasswordValidationResult):
        lower = password.lower().strip()
        if lower in COMMON_PASSWORDS:
            result.reject(
                PasswordErrorCode.COMMON,
                "Esta contraseña es demasiado común o fácil de adivinar.",
            )

    def _check_vaner_terms(self, password: str, result: PasswordValidationResult):
        lower = password.lower()
        for term in VANER_TERMS:
            if term in lower:
                result.reject(
                    PasswordErrorCode.CONTAINS_TENANT_DATA,
                    "La contraseña contiene información relacionada con la plataforma.",
                )
                break

    def _check_personal_data(
        self, password: str, usuario: Usuario, result: PasswordValidationResult
    ):
        lower = password.lower()

        username = (usuario.username or "").lower().strip()
        if username and len(username) >= 3 and username in lower:
            result.reject(
                PasswordErrorCode.CONTAINS_USERNAME,
                "La contraseña contiene información relacionada con tu cuenta.",
            )

        email = (usuario.email or "").lower().strip()
        if email:
            local_part = email.split("@")[0]
            if local_part and len(local_part) >= 3 and local_part in lower:
                result.reject(
                    PasswordErrorCode.CONTAINS_EMAIL,
                    "La contraseña contiene información relacionada con tu cuenta.",
                )

    def _check_history(
        self, password: str, usuario: Usuario, db: Session, result: PasswordValidationResult
    ):
        from app.models.password_history import PasswordHistory
        from app.security import verify_password

        history_count = self.policy["history_count"]
        recent = (
            db.query(PasswordHistory)
            .filter(PasswordHistory.usuario_id == usuario.id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(history_count)
            .all()
        )

        for entry in recent:
            if verify_password(password, entry.password_hash):
                result.reject(
                    PasswordErrorCode.RECENTLY_USED,
                    f"Esta contraseña fue utilizada en las últimas {history_count} veces.",
                )
                break


# Instancia global reutilizable
password_policy = PasswordPolicyService()
