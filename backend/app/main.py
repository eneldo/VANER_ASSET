# =========================================================
# MAIN BACKEND SGA PRO
# Punto principal de entrada de FastAPI
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings

# Routers del sistema
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


# Crear instancia FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


# =========================================================
# CORS PARA FRONTEND REACT
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir al dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ARCHIVOS ESTÁTICOS
# =========================================================

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads"
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

@app.get("/")
def root():
    """
    Ruta inicial para comprobar que el backend está activo.
    """
    return {
        "message": "Backend SGA PRO funcionando correctamente",
        "version": "1.0.0",
        "fase": "Hoja de vida tecnica completa"
    }