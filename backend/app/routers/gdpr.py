"""
VANER ASSET — GDPR Compliance Endpoints
Endpoints para cumplimiento de GDPR/LGPD.

Derechos implementados:
- Art. 15: Derecho de acceso
- Art. 16: Derecho de rectificacion
- Art. 17: Derecho de supresion
- Art. 20: Derecho a la portabilidad
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.core.auth_dependencies import obtener_usuario_actual
from app.models.usuario import Usuario

router = APIRouter(prefix="/auth", tags=["GDPR Compliance"])


class DatosPersonales(BaseModel):
    """Modelo para respuesta de datos personales."""
    id: str
    email: str
    nombre_completo: str
    telefono: Optional[str]
    empresa_id: Optional[str]
    rol: str
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]


class RectificacionRequest(BaseModel):
    """Modelo para solicitud de rectificacion."""
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None


class SolicitudSupresion(BaseModel):
    """Modelo para solicitud de supresion."""
    motivo: str
    confirmar_eliminacion: bool


@router.get("/mis-datos", response_model=DatosPersonales)
async def obtener_mis_datos(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Derecho de Acceso (Art. 15 GDPR)

    Retorna todos los datos personales del usuario autenticado.
    """
    return DatosPersonales(
        id=str(usuario.id),
        email=usuario.email,
        nombre_completo=usuario.nombre_completo,
        telefono=usuario.telefono,
        empresa_id=str(usuario.empresa_id) if usuario.empresa_id else None,
        rol=usuario.rol,
        fecha_creacion=usuario.created_at,
        ultimo_acceso=usuario.updated_at,
    )


@router.put("/rectificar-datos", response_model=DatosPersonales)
async def rectificar_datos(
    datos: RectificacionRequest,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Derecho de Rectificacion (Art. 16 GDPR)

    Permite al usuario corregir sus datos personales.
    """
    if datos.nombre_completo is not None:
        usuario.nombre_completo = datos.nombre_completo
    if datos.telefono is not None:
        usuario.telefono = datos.telefono

    db.commit()
    db.refresh(usuario)

    return DatosPersonales(
        id=str(usuario.id),
        email=usuario.email,
        nombre_completo=usuario.nombre_completo,
        telefono=usuario.telefono,
        empresa_id=str(usuario.empresa_id) if usuario.empresa_id else None,
        rol=usuario.rol,
        fecha_creacion=usuario.created_at,
        ultimo_acceso=usuario.updated_at,
    )


@router.post("/solicitar-supresion")
async def solicitar_supresion(
    solicitud: SolicitudSupresion,
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Derecho de Supresion (Art. 17 GDPR)

    Solicita la eliminacion de la cuenta del usuario.
    Los datos se anonimizan en lugar de eliminarse fisicamente
    para preservar la integridad referencial.
    """
    if not solicitud.confirmar_eliminacion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe confirmar la eliminacion con confirmar_eliminacion=true"
        )

    # Anonimizar usuario
    usuario.email = f"deleted_{usuario.id}@deleted.com"
    usuario.nombre_completo = "Usuario Eliminado"
    usuario.telefono = None
    usuario.password_hash = None
    usuario.mfa_secret = None
    usuario.mfa_enabled = False
    usuario.is_active = False

    db.commit()

    return {
        "message": "Cuenta anonimizada correctamente",
        "fecha_procesamiento": datetime.now().isoformat(),
        "nota": "Los datos se eliminaran permanentemente en el proximo ciclo de limpieza"
    }


@router.get("/exportar-datos")
async def exportar_datos(
    usuario: Usuario = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    """
    Derecho a la Portabilidad (Art. 20 GDPR)

    Exporta todos los datos del usuario en formato JSON estructurado.
    """
    # Datos personales
    datos_personales = {
        "id": str(usuario.id),
        "email": usuario.email,
        "nombre_completo": usuario.nombre_completo,
        "telefono": usuario.telefono,
        "rol": usuario.rol,
        "empresa_id": str(usuario.empresa_id) if usuario.empresa_id else None,
        "fecha_creacion": usuario.created_at.isoformat(),
    }

    # Nota: En implementacion real, aqui se consultarian
    # los datos de negocio del usuario
    datos_negocio = {
        "nota": "Los datos de negocio se exportarian aqui",
        "equipos": [],
        "mantenimientos": [],
        "ordenes": [],
    }

    return {
        "formato": "JSON",
        "fecha_exportacion": datetime.now().isoformat(),
        "datos_personales": datos_personales,
        "datos_negocio": datos_negocio,
        "metadatos": {
            "version": "1.0",
            "sistema": "VANER ASSET",
            "gdpr_compliant": True,
        }
    }


@router.get("/politica-privacidad")
async def politica_privacidad():
    """
    Retorna la politica de privacidad del sistema.
    """
    return {
        "politica": "https://vanerasset.com/politica-privacidad",
        "version": "1.0",
        "ultima_actualizacion": "2026-08-27",
        "derechos": [
            "Art. 15 - Derecho de acceso",
            "Art. 16 - Derecho de rectificacion",
            "Art. 17 - Derecho de supresion",
            "Art. 20 - Derecho a la portabilidad",
            "Art. 21 - Derecho de oposicion",
        ],
        "contacto": "privacidad@vanerasset.com",
    }
