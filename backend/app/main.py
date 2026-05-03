# =========================================================
# MAIN BACKEND SGA PRO
# Punto principal de entrada de FastAPI
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Routers del sistema
from app.routers import auth
from app.routers import usuarios
from app.routers import empresas
from app.routers import sedes


# Crear instancia FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)


# Configuración CORS para permitir conexión con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción limitar al dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registrar rutas del sistema
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(empresas.router)
app.include_router(sedes.router)


@app.get("/")
def root():
    """
    Ruta inicial para comprobar que el backend está activo.
    """
    return {
        "message": "Backend SGA PRO funcionando correctamente",
        "version": "1.0.0",
        "fase": "Fase 2 - Empresas y Sedes"
    }