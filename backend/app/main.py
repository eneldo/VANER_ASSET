# =========================================================
# MAIN BACKEND SGA PRO
# Archivo: backend/app/main.py
# =========================================================

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.rate_limit import InMemoryRateLimitMiddleware as RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.automation.scheduler import iniciar_scheduler_sga, detener_scheduler_sga


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
from app.routers import configuracion_saas
from app.routers import automatizacion
from app.routers import backups_inteligentes
from app.routers import monitor_vps
from app.routers import smtp_inteligente  # Fase 34.2.3 - SMTP Inteligente SaaS PRO
from app.routers import logs_inteligentes  # Fase 34.2.4 - Logs Inteligentes SaaS PRO
from app.routers import devops_saas  # Fase 34.2.5 - DevOps SaaS PRO
from app.routers import scheduler_inteligente  # Fase 34.2.6 - Scheduler Inteligente SaaS PRO
from app.routers import recovery_restore  # Fase 34.2.7 - Recovery & Restore SaaS PRO
from app.routers import multiempresa_enterprise  # Fase 34.2.8 - Multiempresa & Enterprise SaaS PRO





# =========================================================
# CREAR INSTANCIA FASTAPI
# =========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)


# =========================================================
# MIDDLEWARES DE SEGURIDAD
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuditMiddleware)


# =========================================================
# ARCHIVOS ESTÁTICOS / UPLOADS
# =========================================================
# Ruta correcta en tu proyecto local:
#   C:\Proyectos\SGA_SaaS\backend\app\uploads\evidencias
#
# Ruta correcta dentro del contenedor Docker:
#   /app/app/uploads/evidencias
#
# IMPORTANTE:
#   En Dokploy debe estar:
#   UPLOAD_DIR=/app/app/uploads
# =========================================================

UPLOADS_DIR = Path(os.getenv("UPLOAD_DIR") or "/app/app/uploads").resolve()
EVIDENCIAS_DIR = UPLOADS_DIR / "evidencias"
LOGOS_DIR = UPLOADS_DIR / "logos"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCIAS_DIR.mkdir(parents=True, exist_ok=True)
LOGOS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
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
app.include_router(configuracion_saas.router)
app.include_router(automatizacion.router)
app.include_router(auditoria_pro.router)
app.include_router(backups_inteligentes.router)
app.include_router(smtp_inteligente.router)
app.include_router(monitor_vps.router)
app.include_router(logs_inteligentes.router)
app.include_router(devops_saas.router)
app.include_router(scheduler_inteligente.router)
app.include_router(recovery_restore.router)
app.include_router(multiempresa_enterprise.router)
# =========================================================
# FASE 34.2.1 - SCHEDULER AUTOMATIZACIÓN SAAS PRO
# =========================================================

@app.on_event("startup")
def startup_automatizacion_saas():
    """Inicia el scheduler SaaS sin afectar módulos existentes."""
    iniciar_scheduler_sga()


@app.on_event("shutdown")
def shutdown_automatizacion_saas():
    """Detiene el scheduler de forma segura al apagar FastAPI."""
    detener_scheduler_sga()


# =========================================================
# RUTA BASE
# =========================================================

@app.get("/")
def root():
    """Ruta inicial para comprobar que el backend está activo."""
    return {
        "message": "Backend SGA PRO funcionando correctamente",
        "version": "1.0.0",
        "fase": "34.2.3 - SMTP Inteligente SaaS PRO",
        "uploads_dir": str(UPLOADS_DIR),
    }