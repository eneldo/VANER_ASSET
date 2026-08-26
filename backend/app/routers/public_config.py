from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings
from app.product import COMPANY_NAME, PRODUCT_DESCRIPTION, PRODUCT_NAME


router = APIRouter(prefix="/public", tags=["Configuración pública"])


def public_config_payload() -> dict:
    return {
        "appName": settings.APP_NAME,
        "clientCode": settings.CLIENT_CODE,
        "clientName": settings.CLIENT_NAME,
        "appDomain": settings.APP_DOMAIN,
        "coreCompanyName": COMPANY_NAME,
        "coreProductName": PRODUCT_NAME,
        "description": PRODUCT_DESCRIPTION,
    }


@router.get("/config")
def get_public_config():
    return public_config_payload()


@router.get("/manifest.webmanifest", include_in_schema=False)
def get_web_manifest():
    client_suffix = f" - {settings.CLIENT_NAME}" if settings.CLIENT_NAME else ""
    return JSONResponse(
        content={
            "name": f"{settings.APP_NAME}{client_suffix}",
            "short_name": settings.APP_NAME,
            "description": PRODUCT_DESCRIPTION,
            "id": f"/?client={settings.CLIENT_CODE}",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "background_color": "#f8fafc",
            "theme_color": "#0f172a",
            "orientation": "any",
            "icons": [
                {
                    "src": "/vaner-asset-logo.svg",
                    "sizes": "any",
                    "type": "image/svg+xml",
                    "purpose": "any maskable",
                }
            ],
        },
        media_type="application/manifest+json",
    )
