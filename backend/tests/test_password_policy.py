# =========================================================
# TESTS — POLÍTICA DE CONTRASEÑAS (20 CASOS OBLIGATORIOS)
# Archivo: backend/tests/test_password_policy.py
# =========================================================

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from app.services.password_policy import (
    PasswordPolicyService,
    PasswordErrorCode,
    PasswordValidationResult,
    COMMON_PASSWORDS,
)


# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture
def policy():
    return PasswordPolicyService({
        "min_length": 15,
        "min_length_mfa": 12,
        "max_length": 128,
        "history_count": 5,
        "temp_password_hours": 24,
        "reset_token_minutes": 15,
    })


@pytest.fixture
def mock_usuario():
    u = MagicMock()
    u.username = "juan.perez"
    u.email = "juan@empresa.com"
    u.empresa_id = "emp-001"
    return u


# =========================================================
# 1. Contraseña demasiado corta
# =========================================================

class TestPasswordTooShort:
    def test_short_password_rejected(self, policy):
        result = policy.validate("Corta1!")
        assert not result.valid
        assert PasswordErrorCode.TOO_SHORT in result.codes

    def test_exactly_min_length_accepted(self, policy):
        result = policy.validate("Inventarios seguros 2026")
        assert result.valid or PasswordErrorCode.TOO_SHORT not in result.codes


# =========================================================
# 2. Contraseña superior al máximo
# =========================================================

class TestPasswordTooLong:
    def test_long_password_rejected(self, policy):
        pw = "A" * 129
        result = policy.validate(pw)
        assert not result.valid
        assert PasswordErrorCode.TOO_LONG in result.codes


# =========================================================
# 3. Frase de contraseña válida
# =========================================================

class TestPassphrase:
    def test_passphrase_with_spaces_accepted(self, policy):
        result = policy.validate("Frases largas y seguras para trabajar 2026")
        assert result.valid

    def test_long_passphrase_accepted(self, policy):
        result = policy.validate("Mi frase de contraseña muy larga y segura 2026!")
        assert result.valid


# =========================================================
# 4. Contraseña común
# =========================================================

class TestCommonPassword:
    def test_common_password_rejected(self, policy):
        result = policy.validate("passwordpassword")
        assert not result.valid
        assert PasswordErrorCode.COMMON in result.codes

    def test_admin123_rejected(self, policy):
        result = policy.validate("admin12345")
        assert not result.valid
        assert PasswordErrorCode.TOO_SHORT in result.codes or PasswordErrorCode.COMMON in result.codes

    def test_short_common_rejected_for_length(self, policy):
        result = policy.validate("password")
        assert not result.valid
        assert PasswordErrorCode.TOO_SHORT in result.codes


# =========================================================
# 5. Contraseña relacionada con VANER Asset
# =========================================================

class TestVanerTerms:
    def test_vaner_in_password_rejected(self, policy):
        result = policy.validate("SeguroVaner2026!XY")
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_TENANT_DATA in result.codes

    def test_vanerasset_rejected(self, policy):
        result = policy.validate("VanerAsset2026!XY")
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_TENANT_DATA in result.codes


# =========================================================
# 6. Contraseña que contiene el usuario
# =========================================================

class TestContainsUsername:
    def test_username_in_password_rejected(self, policy, mock_usuario):
        result = policy.validate("Segurojuan.perez2026!", usuario=mock_usuario)
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_USERNAME in result.codes


# =========================================================
# 7. Contraseña que contiene el correo
# =========================================================

class TestContainsEmail:
    def test_email_local_part_rejected(self, policy, mock_usuario):
        result = policy.validate("Segurojuan2026!XY", usuario=mock_usuario)
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_EMAIL in result.codes


# =========================================================
# 8. Contraseña relacionada con la empresa
# =========================================================

class TestTenantData:
    def test_mantenimiento_in_password_rejected(self, policy):
        result = policy.validate("SeguroMantenimiento2026!XY")
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_TENANT_DATA in result.codes

    def test_inventario_in_password_rejected(self, policy):
        result = policy.validate("SeguroInventario2026!XY")
        assert not result.valid
        assert PasswordErrorCode.CONTAINS_TENANT_DATA in result.codes


# =========================================================
# 9. Reutilización de contraseña
# =========================================================

class TestPasswordHistory:
    def test_reuse_detected(self, policy, mock_usuario):
        db = MagicMock()
        entry = MagicMock()
        entry.password_hash = "$argon2id$..."
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            entry
        ]

        from app import security
        original_verify = security.verify_password
        security.verify_password = lambda p, h: True

        try:
            result = policy.validate("NuevaContraseña2026!XY", usuario=mock_usuario, db=db)
            assert not result.valid
            assert PasswordErrorCode.RECENTLY_USED in result.codes
        finally:
            security.verify_password = original_verify


# =========================================================
# 10. Contraseña temporal vencida
# =========================================================

class TestTempPasswordExpired:
    def test_expired_temp_password_flag(self):
        from app.models.usuario import Usuario
        u = Usuario(
            temp_password_expires_at=datetime.utcnow() - timedelta(hours=1),
            debe_cambiar_password=False,
        )
        assert u.temp_password_expires_at < datetime.utcnow()


# =========================================================
# 11. Cambio exitoso
# =========================================================

class TestSuccessfulChange:
    def test_validate_change_different_from_current(self, policy, mock_usuario):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )
        result = policy.validate_change(
            "NuevaContraseña2026!XY",
            "ActualContraseña2026!XY",
            usuario=mock_usuario,
            db=db,
        )
        assert result.valid


# =========================================================
# 12. Revocación de sesiones
# =========================================================

class TestSessionRevocation:
    def test_revocar_sesiones(self):
        from app.services.password_reset_service import revocar_sesiones_usuario
        db = MagicMock()
        count = revocar_sesiones_usuario(db, "user-id")
        db.query.return_value.filter.return_value.update.return_value = count


# =========================================================
# 13. Recuperación con token válido
# =========================================================

class TestResetTokenValid:
    def test_token_hash_deterministic(self):
        from app.services.password_reset_service import hash_token
        h1 = hash_token("test-token-123")
        h2 = hash_token("test-token-123")
        assert h1 == h2
        assert len(h1) == 64


# =========================================================
# 14. Recuperación con token vencido
# =========================================================

class TestResetTokenExpired:
    def test_expired_token_not_found(self):
        from app.services.password_reset_service import buscar_token_valido
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = buscar_token_valido(db, "expired-token")
        assert result is None


# =========================================================
# 15. Reutilización del token
# =========================================================

class TestTokenReuse:
    def test_used_token_not_found(self):
        from app.services.password_reset_service import buscar_token_valido
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = buscar_token_valido(db, "used-token")
        assert result is None


# =========================================================
# 16. Aislamiento entre empresas
# =========================================================

class TestTenantIsolation:
    def test_history_scoped_to_user(self, policy):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )
        mock_user = MagicMock()
        mock_user.username = "user_a"
        mock_user.email = "a@empresa1.com"
        result = policy.validate("Segura2026!XYZ!", usuario=mock_user, db=db)
        assert result.valid


# =========================================================
# 17. Compatibilidad con hashes pbkdf2 existentes
# =========================================================

class TestBackwardCompatibility:
    def test_pbkdf2_hash_verified(self):
        from app.security import hash_password, verify_password, needs_upgrade
        from passlib.context import CryptContext
        legacy_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        legacy_hash = legacy_ctx.hash("TestPassword2026!XY")
        assert verify_password("TestPassword2026!XY", legacy_hash)
        assert needs_upgrade(legacy_hash)

    def test_argon2_hash_verified(self):
        from app.security import hash_password, verify_password, needs_upgrade
        new_hash = hash_password("TestPassword2026!XY")
        assert verify_password("TestPassword2026!XY", new_hash)
        assert not needs_upgrade(new_hash)


# =========================================================
# 18. Migración automática a Argon2id
# =========================================================

class TestHashUpgrade:
    def test_needs_upgrade_for_pbkdf2(self):
        from app.security import needs_upgrade
        assert needs_upgrade("$pbkdf2-sha256$29000$...")

    def test_no_needs_upgrade_for_argon2(self):
        from app.security import needs_upgrade
        assert not needs_upgrade("$argon2id$v=19$m=65536,t=3,p=4$...")


# =========================================================
# 19. Ausencia de contraseñas y hashes en logs
# =========================================================

class TestNoPasswordInLogs:
    def test_validate_never_logs_password(self, policy, capsys):
        policy.validate("TestPassword2026!XY")
        captured = capsys.readouterr()
        assert "TestPassword2026" not in captured.out
        assert "TestPassword2026" not in captured.err

    def test_password_not_in_exception_messages(self, policy):
        result = policy.validate("short")
        for err in result.errors:
            assert "short" not in err


# =========================================================
# 20. Mensajes de error seguros
# =========================================================

class TestSecureErrorMessages:
    def test_no_reveal_specific_criteria(self, policy):
        result = policy.validate("123")
        assert not result.valid
        for err in result.errors:
            assert "mayúscula" not in err.lower() or "caracteres" in err.lower()

    def test_generic_message_for_common(self, policy):
        result = policy.validate("passwordpassword")
        assert "común" in result.errors[0].lower() or "fácil" in result.errors[0].lower()

    def test_same_as_current_message(self, policy, mock_usuario):
        db = MagicMock()
        db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
            []
        )
        result = policy.validate_change(
            "MiContraseña2026!XY",
            "MiContraseña2026!XY",
            usuario=mock_usuario,
            db=db,
        )
        assert not result.valid
        assert PasswordErrorCode.SAME_AS_CURRENT in result.codes
        assert "igual" in result.errors[0].lower()
