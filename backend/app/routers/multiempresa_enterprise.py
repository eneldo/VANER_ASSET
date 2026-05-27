from fastapi import APIRouter

router = APIRouter(
    prefix="/multiempresa-enterprise",
    tags=["Multiempresa Enterprise PRO"]
)

@router.get("/dashboard")
def dashboard_multiempresa():
    return {
        "success": True,
        "empresas": 4,
        "usuarios": 37,
        "equipos": 320,
        "mantenimientos": 120
    }