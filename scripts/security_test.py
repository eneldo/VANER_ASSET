#!/usr/bin/env python3
"""
VANER ASSET — Test de Seguridad API
Ejecuta verificaciones de seguridad contra el backend.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

findings = []


def test_no_debug_endpoints():
    """Verifica que no haya endpoints de debug expuestos."""
    response = client.get("/docs")
    if response.status_code == 200:
        findings.append({
            "severity": "MEDIUM",
            "issue": "Swagger UI expuesto",
            "detail": "/docs está accesible",
            "recommendation": "Deshabilitar en producción"
        })
    else:
        print("[OK] Swagger UI no expuesto")


def test_no_admin_endpoints_without_auth():
    """Verifica que endpoints admin requieran autenticación."""
    admin_paths = [
        "/empresas/", "/sedes/", "/tecnicos/", "/mantenimientos/",
        "/usuarios/", "/permisos/", "/backups-inteligentes/",
    ]
    unprotected = []
    for path in admin_paths:
        response = client.get(path)
        if response.status_code != 401:
            unprotected.append(path)
    
    if unprotected:
        findings.append({
            "severity": "HIGH",
            "issue": "Endpoints admin sin protección",
            "detail": f"Paths sin auth: {unprotected}",
            "recommendation": "Asegurar todos los endpoints admin con require_roles"
        })
    else:
        print("[OK] Todos los endpoints admin requieren autenticacion")


def test_rate_limiting_headers():
    """Verifica que los headers de seguridad estén presentes."""
    response = client.get("/")
    security_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
    ]
    missing = [h for h in security_headers if h not in response.headers]
    if missing:
        findings.append({
            "severity": "LOW",
            "issue": "Headers de seguridad faltantes",
            "detail": f"Headers faltantes: {missing}",
            "recommendation": "Agregar headers de seguridad en middleware"
        })
    else:
        print("[OK] Headers de seguridad presentes")


def test_cors_configuration():
    """Verifica que CORS esté configurado correctamente."""
    response = client.options("/", headers={
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET"
    })
    if "access-control-allow-origin" in response.headers:
        origin = response.headers["access-control-allow-origin"]
        if origin == "*":
            findings.append({
                "severity": "MEDIUM",
                "issue": "CORS permite todos los orígenes",
                "detail": "CORS configured with wildcard *",
                "recommendation": "Restringir orígenes en producción"
            })
        else:
            print(f"[OK] CORS configurado: {origin}")
    else:
        print("[OK] CORS no permite origen malicioso")


def test_error_handling():
    """Verifica que los errores no expongan información sensible."""
    response = client.get("/nonexistent-endpoint-12345")
    if response.status_code == 200:
        findings.append({
            "severity": "LOW",
            "issue": "Error handling inusual",
            "detail": "Endpoint inexistente retorna 200",
            "recommendation": "Verificar error handling"
        })
    else:
        print(f"[OK] Error handling correcto: {response.status_code}")


def test_sql_injection_basic():
    """Test básico de SQL injection."""
    payload = "'; DROP TABLE usuarios; --"
    response = client.get(f"/equipos/?search={payload}")
    if response.status_code == 500:
        findings.append({
            "severity": "HIGH",
            "issue": "Posible SQL injection",
            "detail": "Payload SQL causa error 500",
            "recommendation": "Usar queries parametrizados"
        })
    else:
        print("[OK] SQL injection básico manejado correctamente")


def test_health_endpoints():
    """Verifica que health checks estén configurados."""
    response_live = client.get("/health/live")
    response_ready = client.get("/health/ready")
    
    if response_live.status_code == 200 and response_ready.status_code == 200:
        print("[OK] Health checks configurados")
    else:
        findings.append({
            "severity": "MEDIUM",
            "issue": "Health checks no funcionales",
            "detail": f"live: {response_live.status_code}, ready: {response_ready.status_code}",
            "recommendation": "Implementar health checks completos"
        })


def test_metrics_endpoint():
    """Verifica que el endpoint de métricas exista."""
    response = client.get("/metrics")
    if response.status_code == 200:
        print("[OK] Endpoint /metrics disponible")
    else:
        findings.append({
            "severity": "LOW",
            "issue": "Endpoint /metrics no disponible",
            "detail": f"Status: {response.status_code}",
            "recommendation": "Implementar métricas básicas"
        })


if __name__ == "__main__":
    print("=" * 60)
    print("VANER ASSET — Test de Seguridad API")
    print("=" * 60)
    print()
    
    test_no_debug_endpoints()
    test_no_admin_endpoints_without_auth()
    test_rate_limiting_headers()
    test_cors_configuration()
    test_error_handling()
    test_sql_injection_basic()
    test_health_endpoints()
    test_metrics_endpoint()
    
    print()
    print("=" * 60)
    if findings:
        print(f"HALLAZGOS: {len(findings)}")
        for f in findings:
            print(f"  [{f['severity']}] {f['issue']}")
            print(f"    {f['detail']}")
            print(f"    Recomendación: {f['recommendation']}")
            print()
    else:
        print("[OK] TODOS LOS TESTS PASARON")
    print("=" * 60)
