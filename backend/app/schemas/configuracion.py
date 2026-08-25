# ============================================================
# SCHEMAS: Configuracion PRO SaaS
# Archivo: backend/app/schemas/configuracion.py
# ============================================================

from typing import Optional
from pydantic import BaseModel, Field
from app.product import PRODUCT_NAME


class ConfiguracionBase(BaseModel):
    # Datos plataforma
    nombre_plataforma: str = Field(default=PRODUCT_NAME, max_length=150)
    empresa_propietaria: Optional[str] = None
    nit: Optional[str] = None
    correo_soporte: Optional[str] = None
    telefono_soporte: Optional[str] = None
    url_plataforma: Optional[str] = None
    logo_url: Optional[str] = None
    color_primario: str = "#2563eb"
    color_secundario: str = "#0f172a"

    # Seguridad
    intentos_login: int = 5
    minutos_bloqueo: int = 15
    expiracion_token_min: int = 60
    exigir_password_seguro: bool = True
    doble_factor_activo: bool = False
    auditoria_activa: bool = True

    # Evidencias
    max_tamano_evidencia_mb: int = 10
    permitir_pdf: bool = True
    permitir_imagenes: bool = True
    ruta_evidencias: str = "app/uploads/evidencias"
    retencion_evidencias_dias: int = 365

    # Backups
    backups_activos: bool = True
    frecuencia_backup: str = "DIARIO"
    hora_backup: str = "02:00"
    ruta_backup: str = "app/backups"
    retencion_backups_dias: int = 30

    # Mantenimiento
    dias_alerta_mantenimiento: int = 7
    permitir_mantenimiento_vencido: bool = True
    requiere_evidencia_cierre: bool = True
    requiere_observacion_cierre: bool = True
    estados_mantenimiento: str = "PROGRAMADO,ASIGNADO,EN_PROCESO,PAUSADO,FINALIZADO,ANULADO"

    # Notificaciones
    notificaciones_activas: bool = True
    notificar_email: bool = True
    notificar_whatsapp: bool = False
    dias_antes_notificar: int = 3
    email_remitente: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_puerto: Optional[int] = None
    smtp_usuario: Optional[str] = None
    smtp_password: Optional[str] = None


class ConfiguracionCreate(ConfiguracionBase):
    pass


class ConfiguracionUpdate(ConfiguracionBase):
    pass


class ConfiguracionOut(ConfiguracionBase):
    id: int

    class Config:
        from_attributes = True
