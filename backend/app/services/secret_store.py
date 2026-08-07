from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

ENCRYPTED_PREFIX = "enc:v1:"
MASKED_SECRET = "********"


def _fernet() -> Fernet:
    if not settings.CONFIG_ENCRYPTION_KEY:
        raise RuntimeError("CONFIG_ENCRYPTION_KEY is not configured")
    return Fernet(settings.CONFIG_ENCRYPTION_KEY.encode("ascii"))


def encrypt_secret(value: str | None) -> str:
    plain_value = str(value or "")
    if not plain_value or plain_value.startswith(ENCRYPTED_PREFIX):
        return plain_value
    encrypted = _fernet().encrypt(plain_value.encode("utf-8")).decode("ascii")
    return f"{ENCRYPTED_PREFIX}{encrypted}"


def decrypt_secret(value: str | None) -> str:
    stored_value = str(value or "")
    if not stored_value or not stored_value.startswith(ENCRYPTED_PREFIX):
        return stored_value
    token = stored_value[len(ENCRYPTED_PREFIX):]
    try:
        return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Stored secret cannot be decrypted with CONFIG_ENCRYPTION_KEY") from exc


def merge_secret(existing: str | None, incoming: str | None) -> str:
    if incoming in (None, "", MASKED_SECRET):
        return str(existing or "")
    return encrypt_secret(incoming)


def mask_secret(value: str | None) -> str:
    return MASKED_SECRET if value else ""


def decrypt_mapping(data: dict | None, fields: set[str]) -> dict:
    result = dict(data or {})
    for field in fields:
        if field in result:
            result[field] = decrypt_secret(result.get(field))
    return result
