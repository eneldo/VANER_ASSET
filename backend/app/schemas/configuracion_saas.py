# ============================================================
# SCHEMAS: Configuración Inteligente SaaS
# Archivo: backend/app/schemas/configuracion_saas.py
# Fase 34.1 - Configuración Inteligente SaaS PRO
# ============================================================

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, EmailStr


class SMTPConfig(BaseModel):
    host: str = ""
    port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    from_name: str = "SGA SaaS PRO"
    use_tls: bool = True
    use_ssl: bool = False


class BackupConfig(BaseModel):
    habilitado: bool = True
    frecuencia: str = "DIARIO"  # DIARIO, SEMANAL, MENSUAL
    hora: str = "02:00"
    retencion_dias: int = 30
    incluir_evidencias: bool = True
    ruta_destino: str = "app/exports/backups"


class EvidenciasConfig(BaseModel):
    max_mb: int = 15
    formatos_permitidos: list[str] = Field(default_factory=lambda: ["jpg", "jpeg", "png", "pdf", "webp"])
    requiere_descripcion: bool = False
    permitir_pdf: bool = True
    permitir_imagen: bool = True
    compresion_imagen: bool = True
    compresion_pdf: bool = True
    calidad_imagen: int = Field(default=82, ge=50, le=95)
    max_dimension_imagen: int = Field(default=2048, ge=800, le=4096)


class MantenimientoConfig(BaseModel):
    dias_alerta_vencimiento: int = 3
    permitir_reprogramacion: bool = True
    requiere_evidencia_finalizar: bool = True
    requiere_observacion_finalizar: bool = True
    estados_permitidos: list[str] = Field(default_factory=lambda: [
        "PROGRAMADO", "ASIGNADO", "EN_PROCESO", "PAUSADO", "FINALIZADO", "ANULADO"
    ])


class NotificacionesConfig(BaseModel):
    email_habilitado: bool = True
    whatsapp_habilitado: bool = False
    whatsapp_provider: str = ""
    whatsapp_token: str = ""
    notificar_asignacion: bool = True
    notificar_vencimiento: bool = True
    notificar_finalizacion: bool = True
    notificar_cliente: bool = True
    correos_copia: list[str] = Field(default_factory=list)


class ConfiguracionSaaSBase(BaseModel):
    nombre_plataforma: str = "SGA SaaS PRO"
    logo_url: Optional[str] = None
    color_primario: str = "#2563eb"
    color_secundario: str = "#0f172a"
    color_acento: str = "#22c55e"
    smtp: SMTPConfig = Field(default_factory=SMTPConfig)
    backups: BackupConfig = Field(default_factory=BackupConfig)
    evidencias: EvidenciasConfig = Field(default_factory=EvidenciasConfig)
    mantenimiento: MantenimientoConfig = Field(default_factory=MantenimientoConfig)
    notificaciones: NotificacionesConfig = Field(default_factory=NotificacionesConfig)


class ConfiguracionSaaSUpdate(ConfiguracionSaaSBase):
    pass


class ConfiguracionSaaSOut(ConfiguracionSaaSBase):
    id: int
    activo: bool

    class Config:
        from_attributes = True


class TestEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str = "Prueba SMTP - SGA SaaS PRO"
    message: str = "Correo de prueba enviado correctamente desde la configuración SGA SaaS PRO."


class ApiResponse(BaseModel):
    ok: bool
    message: str
    data: Optional[Dict[str, Any]] = None
