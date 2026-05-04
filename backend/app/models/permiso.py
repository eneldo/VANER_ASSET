# ============================================================
# MODELOS: Roles, Permisos y relaciones
# Archivo: app/models/permiso.py
# ============================================================

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, server_default=func.now())

    permisos = relationship(
        "RolPermiso",
        back_populates="rol",
        cascade="all, delete-orphan"
    )


class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(80), unique=True, nullable=False, index=True)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text, nullable=True)
    modulo = Column(String(80), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, server_default=func.now())


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permiso_id = Column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False)

    rol = relationship("Rol", back_populates="permisos")
    permiso = relationship("Permiso")


class UsuarioPermiso(Base):
    __tablename__ = "usuarios_permisos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    permiso_id = Column(Integer, ForeignKey("permisos.id", ondelete="CASCADE"), nullable=False)

    permiso = relationship("Permiso")