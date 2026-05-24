# ============================================================
# MODELO: Configuracion PRO SaaS
# Archivo: backend/app/models/configuracion.py
# Descripción:
#   Tabla centralizada para guardar la configuración global
#   de la plataforma SGA SaaS en PostgreSQL.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ConfiguracionSistema(Base):
    """
    Configuración general de la plataforma.

    Se maneja como registro único id=1 para simplificar el panel PRO.
    """

    __tablename__ = "configuracion_sistema"

    id = Column(Integer, primary_key=True, index=True)

    # Datos plataforma
    nombre_plataforma = Column(String(150), nullable=False, default="SGA PRO SaaS")
    empresa_propietaria = Column(String(180), nullable=True)
    nit = Column(String(50), nullable=True)
    correo_soporte = Column(String(160), nullable=True)
    telefono_soporte = Column(String(80), nullable=True)
    url_plataforma = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    color_primario = Column(String(20), nullable=False, default="#2563eb")
    color_secundario = Column(String(20), nullable=False, default="#0f172a")

    # Seguridad
    intentos_login = Column(Integer, nullable=False, default=5)
    minutos_bloqueo = Column(Integer, nullable=False, default=15)
    expiracion_token_min = Column(Integer, nullable=False, default=60)
    exigir_password_seguro = Column(Boolean, nullable=False, default=True)
    doble_factor_activo = Column(Boolean, nullable=False, default=False)
    auditoria_activa = Column(Boolean, nullable=False, default=True)

    # Evidencias
    max_tamano_evidencia_mb = Column(Integer, nullable=False, default=10)
    permitir_pdf = Column(Boolean, nullable=False, default=True)
    permitir_imagenes = Column(Boolean, nullable=False, default=True)
    ruta_evidencias = Column(String(500), nullable=False, default="app/uploads/evidencias")
    retencion_evidencias_dias = Column(Integer, nullable=False, default=365)

    # Backups
    backups_activos = Column(Boolean, nullable=False, default=True)
    frecuencia_backup = Column(String(50), nullable=False, default="DIARIO")
    hora_backup = Column(String(10), nullable=False, default="02:00")
    ruta_backup = Column(String(500), nullable=False, default="app/backups")
    retencion_backups_dias = Column(Integer, nullable=False, default=30)

    # Mantenimiento
    dias_alerta_mantenimiento = Column(Integer, nullable=False, default=7)
    permitir_mantenimiento_vencido = Column(Boolean, nullable=False, default=True)
    requiere_evidencia_cierre = Column(Boolean, nullable=False, default=True)
    requiere_observacion_cierre = Column(Boolean, nullable=False, default=True)
    estados_mantenimiento = Column(Text, nullable=False, default="PROGRAMADO,ASIGNADO,EN_PROCESO,PAUSADO,FINALIZADO,ANULADO")

    # Notificaciones
    notificaciones_activas = Column(Boolean, nullable=False, default=True)
    notificar_email = Column(Boolean, nullable=False, default=True)
    notificar_whatsapp = Column(Boolean, nullable=False, default=False)
    dias_antes_notificar = Column(Integer, nullable=False, default=3)
    email_remitente = Column(String(160), nullable=True)
    smtp_host = Column(String(160), nullable=True)
    smtp_puerto = Column(Integer, nullable=True)
    smtp_usuario = Column(String(160), nullable=True)
    smtp_password = Column(String(255), nullable=True)

    # Auditoría temporal
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
