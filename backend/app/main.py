# =========================================================
# MAIN BACKEND SGA PRO
# Punto principal de entrada de FastAPI
# =========================================================

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

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


# =========================================================
# CREAR INSTANCIA FASTAPI
# =========================================================

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
# ARCHIVOS ESTÁTICOS / UPLOADS
# Objetivo:
#   Permitir visualizar archivos cargados, como:
#   - Evidencias de mantenimiento
#   - Imágenes
#   - PDFs
#
# URL pública:
#   http://127.0.0.1:8000/uploads/evidencias/archivo.png
#
# Carpeta física:
#   backend/app/uploads/
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOADS_DIR, "evidencias"), exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOADS_DIR),
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
app.include_router(cliente.router)




# =========================================================
# RUTA BASE
# =========================================================

@app.get("/")
def root():
    """
    Ruta inicial para comprobar que el backend está activo.
    """
    return {
        "message": "Backend SGA PRO funcionando correctamente",
        "version": "1.0.0",
        "fase": "SGA PRO - Evidencias y mantenimiento"
    }