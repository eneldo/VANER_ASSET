# =========================================================
# MFA — Router para Multi-Factor Authentication
# Archivo: app/routers/mfa.py
# =========================================================

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.auth import obtener_usuario_actual
from app.services.mfa_service import MFAService

router = APIRouter(prefix="/mfa", tags=["MFA"])


class MFASetupResponse(BaseModel):
    secret: str
    uri: str
    backup_codes: list[str]
    message: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFAStatusResponse(BaseModel):
    enabled: bool
    configured: bool
    backup_codes_remaining: int


class MFAMessageResponse(BaseModel):
    success: bool
    message: str


@router.post("/setup", response_model=MFASetupResponse)
def setup_mfa(
    current_user=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Inicializa MFA para el usuario actual.
    Retorna secreto, URI para QR y códigos de respaldo.
    """
    service = MFAService(db)

    # Check if MFA is already configured
    status = service.get_mfa_status(str(current_user.id))
    if status["enabled"]:
        raise HTTPException(
            status_code=400,
            detail="MFA ya está habilitado. Desactívalo primero para reconfigurar."
        )

    try:
        result = service.setup_mfa(str(current_user.id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enable", response_model=MFAMessageResponse)
def enable_mfa(
    request: MFAVerifyRequest,
    current_user=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Activa MFA después de verificar un código válido.
    """
    service = MFAService(db)

    success = service.enable_mfa(str(current_user.id), request.code)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Código inválido. Verifica tu authenticator app e intenta de nuevo."
        )

    return MFAMessageResponse(
        success=True,
        message="MFA habilitado correctamente. Guarda tus códigos de respaldo en un lugar seguro.",
    )


@router.post("/verify", response_model=MFAMessageResponse)
def verify_mfa(
    request: MFAVerifyRequest,
    current_user=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Verifica un código MFA (útil para testing o verificación manual).
    """
    service = MFAService(db)

    success = service.verify_mfa(str(current_user.id), request.code)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Código inválido.",
        )

    return MFAMessageResponse(
        success=True,
        message="Código verificado correctamente.",
    )


@router.post("/disable", response_model=MFAMessageResponse)
def disable_mfa(
    request: MFAVerifyRequest,
    current_user=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Desactiva MFA después de verificar un código válido.
    """
    service = MFAService(db)

    success = service.disable_mfa(str(current_user.id), request.code)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Código inválido o MFA no está habilitado.",
        )

    return MFAMessageResponse(
        success=True,
        message="MFA deshabilitado correctamente.",
    )


@router.get("/status", response_model=MFAStatusResponse)
def get_mfa_status(
    current_user=Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Obtiene el estado MFA del usuario actual.
    """
    service = MFAService(db)
    return service.get_mfa_status(str(current_user.id))
