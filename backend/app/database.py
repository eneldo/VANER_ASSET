# =========================================================
# DATABASE CONFIGURATION
# Archivo: app/database.py
# Configuración SQLAlchemy Profesional
# Compatible con Alembic + PostgreSQL
# =========================================================

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from app.config import settings


# =========================================================
# ENGINE PRINCIPAL
# =========================================================
# pool_pre_ping:
# Verifica conexiones muertas automáticamente
#
# pool_recycle:
# Evita desconexiones por timeout
#
# echo:
# Mostrar SQL en consola (solo desarrollo)
# =========================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)


# =========================================================
# SESSION LOCAL
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def _es_postgresql(session: Session) -> bool:
    """Evita ejecutar funciones PostgreSQL en dobles de prueba u otros motores."""
    bind = session.get_bind()
    return bool(bind is not None and bind.dialect.name == "postgresql")


def establecer_contexto_tenant(session: Session, usuario) -> None:
    """
    Vincula la transacción al tenant autenticado para las políticas RLS.

    Los valores se guardan también en ``session.info`` para restaurarlos cuando
    un endpoint hace commit y SQLAlchemy abre una transacción nueva.
    """
    rol = str(getattr(usuario, "rol", "") or "").upper()
    tenant_id = str(getattr(usuario, "empresa_id", "") or "")
    es_admin = rol == "ADMIN"

    establecer_contexto_empresa(session, tenant_id, es_admin=es_admin)


def establecer_contexto_empresa(
    session: Session,
    empresa_id,
    *,
    es_admin: bool = False,
) -> None:
    tenant_id = str(empresa_id or "")

    if _es_postgresql(session):
        session.execute(
            text(
                "SELECT "
                "set_config('app.current_tenant', :tenant_id, true), "
                "set_config('app.is_platform_admin', :es_admin, true)"
            ),
            {"tenant_id": tenant_id, "es_admin": "true" if es_admin else "false"},
        )

    session.info["rls_tenant_id"] = tenant_id
    session.info["rls_platform_admin"] = es_admin


def establecer_contexto_sistema(session: Session) -> None:
    """Contexto privilegiado y acotado para auditoría/servicios internos."""
    if _es_postgresql(session):
        session.execute(
            text(
                "SELECT set_config('app.current_tenant', '', true), "
                "set_config('app.is_platform_admin', 'true', true)"
            )
        )
    session.info["rls_tenant_id"] = ""
    session.info["rls_platform_admin"] = True


@event.listens_for(Session, "after_begin")
def _restaurar_contexto_tenant(session, transaction, connection):
    """Restaura variables RLS tras cada commit/rollback de la misma sesión."""
    if "rls_platform_admin" not in session.info or connection.dialect.name != "postgresql":
        return

    connection.execute(
        text(
            "SELECT "
            "set_config('app.current_tenant', :tenant_id, true), "
            "set_config('app.is_platform_admin', :es_admin, true)"
        ),
        {
            "tenant_id": session.info.get("rls_tenant_id", ""),
            "es_admin": "true" if session.info.get("rls_platform_admin") else "false",
        },
    )


# =========================================================
# BASE GLOBAL MODELOS
# =========================================================

Base = declarative_base()


# =========================================================
# DEPENDENCIA FASTAPI
# =========================================================

def get_db():
    """
    Genera una sesión de base de datos
    para cada request y la cierra automáticamente.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
