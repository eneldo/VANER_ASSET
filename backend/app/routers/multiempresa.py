from fastapi import APIRouter

router = APIRouter(
    prefix="/multiempresa",
    tags=["Multiempresa Enterprise"]
)

@router.get("/health")
def health():
    return {
        "success": True,
        "multiempresa": True
    }
