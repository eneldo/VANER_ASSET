# =========================================================
# MODELO USUARIO
# Tabla: usuarios
# Maneja login y roles del sistema
# =========================================================

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


usuario_empresas = Table(
    "usuario_empresas",
    Base.metadata,
    Column(
        "usuario_id",
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "empresa_id",
        UUID(as_uuid=True),
        ForeignKey("empresas.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)


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
    rol = Column(String(30), nullable=False, index=True)

    # Empresa asociada, aplica principalmente para rol EMPRESA
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresas.id"), nullable=True, index=True)

    empresas_autorizadas = relationship(
        "Empresa",
        secondary=usuario_empresas,
        lazy="select",
    )

    @property
    def empresa_ids(self):
        ids = [empresa.id for empresa in self.empresas_autorizadas]
        if self.empresa_id and self.empresa_id not in ids:
            ids.insert(0, self.empresa_id)
        return ids

    # Estado del usuario
    activo = Column(Boolean, default=True)

    # Política de contraseñas
    debe_cambiar_password = Column(Boolean, default=False)
    password_changed_at = Column(DateTime, nullable=True)
    temp_password_expires_at = Column(DateTime, nullable=True)

    # Auditoría
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

    # MFA (Multi-Factor Authentication)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_backup_codes = Column(Text, nullable=True)
