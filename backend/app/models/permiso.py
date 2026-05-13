# ================================================================
# SGA PRO - FASE 31.2
# Archivo: backend/app/models/permiso.py
# Objetivo:
#   Modelos SQLAlchemy para roles, permisos y asignaciones.
#   No elimina el campo rol existente en usuarios; lo complementa.
# ================================================================

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


roles_permisos = Table(
    "roles_permisos",
    Base.metadata,
    Column("rol_id", UUID(as_uuid=True), ForeignKey("roles_sistema.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", UUID(as_uuid=True), ForeignKey("permisos_sistema.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


class RolSistema(Base):
    """Catálogo oficial de roles del sistema."""

    __tablename__ = "roles_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(40), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    permisos = relationship("PermisoSistema", secondary=roles_permisos, back_populates="roles")


class PermisoSistema(Base):
    """Permiso granular por módulo y acción."""

    __tablename__ = "permisos_sistema"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = Column(String(80), unique=True, nullable=False, index=True)
    modulo = Column(String(60), nullable=False, index=True)
    accion = Column(String(40), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    roles = relationship("RolSistema", secondary=roles_permisos, back_populates="permisos")


class UsuarioPermiso(Base):
    """Permisos directos por usuario para excepciones puntuales."""

    __tablename__ = "usuarios_permisos"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    permiso_id = Column(UUID(as_uuid=True), ForeignKey("permisos_sistema.id", ondelete="CASCADE"), primary_key=True)
    permitido = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
