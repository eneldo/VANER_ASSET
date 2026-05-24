# ============================================================
# ROUTER: Configuracion PRO SaaS
# Archivo: backend/app/routers/configuracion.py
# Descripción:
#   Endpoints para consultar y actualizar la configuración
#   general del sistema SGA SaaS.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.configuracion import ConfiguracionSistema
from app.schemas.configuracion import ConfiguracionOut, ConfiguracionUpdate

router = APIRouter(prefix="/configuracion", tags=["Configuración PRO SaaS"])


def obtener_o_crear_configuracion(db: Session) -> ConfiguracionSistema:
    """
    Obtiene el registro único de configuración.
    Si no existe, lo crea automáticamente con valores por defecto.
    """
    config = db.query(ConfiguracionSistema).filter(ConfiguracionSistema.id == 1).first()

    if not config:
        config = ConfiguracionSistema(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


@router.get("/", response_model=ConfiguracionOut)
def obtener_configuracion(db: Session = Depends(get_db)):
    """Devuelve la configuración actual del sistema."""
    return obtener_o_crear_configuracion(db)


@router.put("/", response_model=ConfiguracionOut)
def actualizar_configuracion(payload: ConfiguracionUpdate, db: Session = Depends(get_db)):
    """Actualiza la configuración general de la plataforma."""
    config = obtener_o_crear_configuracion(db)

    data = payload.model_dump()

    # Protección básica para evitar valores inválidos críticos.
    if data.get("intentos_login", 1) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Los intentos de login deben ser mayor o igual a 1")

    if data.get("max_tamano_evidencia_mb", 1) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El tamaño máximo de evidencia debe ser mayor o igual a 1 MB")

    for key, value in data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config


@router.post("/restaurar", response_model=ConfiguracionOut)
def restaurar_configuracion(db: Session = Depends(get_db)):
    """
    Restaura la configuración a valores PRO por defecto.
    No elimina empresas, usuarios, equipos ni mantenimientos.
    """
    config = obtener_o_crear_configuracion(db)

    valores_default = ConfiguracionSistema(id=1)
    for column in ConfiguracionSistema.__table__.columns:
        name = column.name
        if name not in ["id", "creado_en", "actualizado_en"]:
            setattr(config, name, getattr(valores_default, name))

    db.commit()
    db.refresh(config)
    return config
