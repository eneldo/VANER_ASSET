# =========================================================
# SCHEMAS DE USUARIOS
# Validan datos para crear usuarios desde la API
# =========================================================

from pydantic import BaseModel, EmailStr


class AdminCreate(BaseModel):
    # Nombre completo del administrador
    nombre_completo: str

    # Usuario para login
    username: str

    # Correo del administrador
    email: EmailStr

    # Contraseña en texto plano que luego será encriptada
    password: str