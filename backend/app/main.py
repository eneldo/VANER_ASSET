# =========================================================
# MAIN BACKEND SGA PRO
# Archivo: backend/app/main.py
# =========================================================
# Fase 31.5:
# - registra router auditoria_pro,
# - activa AuditMiddleware para trazabilidad automática,
# - conserva routers existentes del proyecto.
# =========================================================

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.middleware.audit_middleware import AuditMiddleware

from app.middleware.rate_limit import (
    InMemoryRateLimitMiddleware as RateLimitMiddleware
)

from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


# =========================================================
# ROUTERS DEL SISTEMA
# =========================================================

from app.routers import auth
from app.routers import usuarios
from app.routers import empresas
from app.routers import sedes
from app.routers import categorias
from app.routers import equipos
from app.routers import equipo_hoja_vida
from app.routers import tecnicos
from app.routers import mantenimientos
from app.routers import evidencias
from app.routers import dashboard_tecnico
from app.routers import permisos
from app.routers import cliente
from app.routers import reportes
from app.routers import auditoria
from app.routers import auditoria_pro
from app.routers import password_recovery  
from app.routers import coordinador
from app.routers import formatos_mantenimiento
from app.routers import formatos_dinamicos
from app.routers import bitacoras_dinamicas
from app.routers import configuracion



# =========================================================
# CREAR INSTANCIA FASTAPI
# =========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


# =========================================================
# MIDDLEWARES DE SEGURIDAD
# IMPORTANTE:
#   El orden se conserva estable para evitar romper CORS.
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir al dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Si estos middlewares ya existen desde Fase 31.3, se mantienen activos.
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)

# Fase 31.5 - Auditoría automática HTTP.
app.add_middleware(AuditMiddleware)


# =========================================================
# ARCHIVOS ESTÁTICOS / UPLOADS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "evidencias"), exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
    name="uploads",
)


# =========================================================
# REGISTRO DE ROUTERS
# =========================================================

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(empresas.router)
app.include_router(sedes.router)
app.include_router(categorias.router)
app.include_router(equipos.router)
app.include_router(equipo_hoja_vida.router)
app.include_router(tecnicos.router)
app.include_router(mantenimientos.router)
app.include_router(evidencias.router)
app.include_router(dashboard_tecnico.router)
app.include_router(permisos.router)
app.include_router(cliente.router)
app.include_router(reportes.router)
app.include_router(auditoria.router)
app.include_router(password_recovery.router)
app.include_router(coordinador.router)
app.include_router(formatos_mantenimiento.router)
app.include_router(formatos_dinamicos.router)
app.include_router(bitacoras_dinamicas.router)
app.include_router(configuracion.router)
# Fase 31.5 - Router nuevo de auditoría y monitoreo PRO.
app.include_router(auditoria_pro.router)


# =========================================================
# RUTA BASE
# =========================================================

@app.get("/")
def root():
    """Ruta inicial para comprobar que el backend está activo."""
    return {
        "message": "Backend SGA PRO funcionando correctamente",
        "version": "1.0.0",
        "fase": "31.5 - Auditoría y Monitoreo PRO SaaS",
    }
