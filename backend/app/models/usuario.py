# =========================================================
# MODELO USUARIO
# Tabla: usuarios
# Maneja login y roles del sistema
# =========================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    # Identificador único del usuario
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Datos básicos
    nombre_completo = Column(String(150), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)

    # Contraseña encriptada
    password_hash = Column(String, nullable=False)

    # Roles permitidos:
    # ADMIN, TECNICO, EMPRESA, COORDINADOR
    rol = Column(String(30), nullable=False)

    # Empresa asociada, aplica principalmente para rol EMPRESA
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True)

    # Estado del usuario
    activo = Column(Boolean, default=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())