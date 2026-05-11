# ============================================================
# MODELO: Notificacion
# Archivo: backend/app/models/notificacion.py
# Fase 29 - Notificaciones y Alertas PRO
# ============================================================
# Objetivo:
#   Guardar alertas del sistema para ADMIN, COORDINADOR, TECNICO
#   y CLIENTE/EMPRESA. Estas alertas permiten mostrar vencimientos,
#   mantenimientos atrasados, asignaciones, finalizaciones y mensajes
#   operativos dentro de la plataforma SGA PRO.
# ============================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Notificacion(Base):
    """
    Tabla central de notificaciones internas del sistema.

    Diseño compatible con el proyecto actual:
    - IDs enteros, como mantenimientos/equipos/usuarios existentes.
    - Campos opcionales para relacionar empresa, sede, equipo,
      mantenimiento y técnico sin romper registros antiguos.
    """

    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)

    # Rol destinatario principal: ADMIN, COORDINADOR, TECNICO, EMPRESA, CLIENTE
    rol_destino = Column(String(30), nullable=False, index=True)

    # Usuario específico opcional. Si es NULL, aplica al rol completo.
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relaciones de negocio opcionales para filtros y navegación.
    empresa_id = Column(Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="SET NULL"), nullable=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="SET NULL"), nullable=True, index=True)
    mantenimiento_id = Column(Integer, ForeignKey("mantenimientos.id", ondelete="SET NULL"), nullable=True, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id", ondelete="SET NULL"), nullable=True, index=True)

    # Clasificación visual y funcional.
    tipo = Column(String(40), nullable=False, default="INFO", index=True)
    prioridad = Column(String(20), nullable=False, default="MEDIA", index=True)

    titulo = Column(String(180), nullable=False)
    mensaje = Column(Text, nullable=True)

    # URL interna sugerida para abrir desde la notificación.
    enlace = Column(String(255), nullable=True)

    # Estado de lectura.
    leida = Column(Boolean, nullable=False, default=False, index=True)

    creado_en = Column(DateTime, server_default=func.now(), nullable=False)
    leido_en = Column(DateTime, nullable=True)

    # Relaciones opcionales. No son necesarias para crear la tabla,
    # pero ayudan si luego se quieren serializar datos relacionados.
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    empresa = relationship("Empresa", foreign_keys=[empresa_id])
    sede = relationship("Sede", foreign_keys=[sede_id])
    equipo = relationship("Equipo", foreign_keys=[equipo_id])
    mantenimiento = relationship("Mantenimiento", foreign_keys=[mantenimiento_id])
    tecnico = relationship("Tecnico", foreign_keys=[tecnico_id])
