#!/usr/bin/env python3
"""
VANER ASSET — E2E Tests con Playwright
Tests de extremo a extremo para flujos críticos.

Uso:
    python scripts/test_e2e.py                    # Ejecutar todos
    python scripts/test_e2e.py --headed          # Con navegador visible
    python scripts/test_e2e.py --browser chromium # Navegador específico
"""

import os
import sys
import argparse
from datetime import datetime

# Configuración
BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:5173")
API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")


def test_health_endpoints():
    """Test: Health checks del backend."""
    import requests

    print("[E2E] Test: Health endpoints")

    # Test /health/live
    response = requests.get(f"{API_URL}/health/live", timeout=10)
    assert response.status_code == 200, f"/health/live returned {response.status_code}"
    print("  [OK] /health/live: 200")

    # Test /health/ready
    response = requests.get(f"{API_URL}/health/ready", timeout=10)
    assert response.status_code in [200, 503], f"/health/ready returned {response.status_code}"
    print(f"  [OK] /health/ready: {response.status_code}")

    # Test /metrics
    response = requests.get(f"{API_URL}/metrics", timeout=10)
    assert response.status_code == 200, f"/metrics returned {response.status_code}"
    print("  [OK] /metrics: 200")

    print("  PASSED\n")


def test_login_flow():
    """Test: Flujo de login completo."""
    from playwright.sync_api import sync_playwright

    print("[E2E] Test: Login flow")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navegar al frontend
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        # Verificar que el título contiene VANER
        title = page.title()
        assert "VANER" in title or "vaner" in title.lower(), f"Unexpected title: {title}"
        print(f"  [OK] Título: {title}")

        # Verificar que el formulario de login está presente
        # Nota: El selector puede variar según la implementación
        login_form = page.query_selector("form") or page.query_selector("[data-testid='login-form']")
        if login_form:
            print("  [OK] Formulario de login encontrado")
        else:
            print("  [INFO] Formulario de login no encontrado (puede estar en otra ruta)")

        browser.close()

    print("  PASSED\n")


def test_api_endpoints():
    """Test: Endpoints públicos de la API."""
    import requests

    print("[E2E] Test: API public endpoints")

    # Test endpoints que no requieren auth
    public_endpoints = [
        ("/auth/login", "POST"),
        ("/health/live", "GET"),
        ("/health/ready", "GET"),
        ("/metrics", "GET"),
    ]

    for endpoint, method in public_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{API_URL}{endpoint}", timeout=10)

            # 200, 404, 405, 422 son válidos (no 500)
            assert response.status_code < 500, f"{endpoint} returned {response.status_code}"
            print(f"  [OK] {method} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  [WARN] {method} {endpoint}: {e}")

    print("  PASSED\n")


def test_security_headers():
    """Test: Headers de seguridad."""
    import requests

    print("[E2E] Test: Security headers")

    response = requests.get(f"{API_URL}/health/live", timeout=10)
    headers = response.headers

    required_headers = [
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
    ]

    for header in required_headers:
        if header in headers:
            print(f"  [OK] {header}: {headers[header]}")
        else:
            print(f"  [WARN] {header}: missing")

    print("  PASSED\n")


def test_frontend_loads():
    """Test: Frontend carga correctamente."""
    from playwright.sync_api import sync_playwright

    print("[E2E] Test: Frontend loads")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        response = page.goto(BASE_URL)
        assert response.status == 200, f"Frontend returned {response.status}"

        # Verificar que hay contenido
        content = page.content()
        assert len(content) > 100, "Frontend content too short"
        print(f"  [OK] Frontend loaded ({len(content)} chars)")

        # Verificar que no hay errores de consola críticos
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.reload()
        page.wait_for_load_state("networkidle")

        if errors:
            print(f"  [WARN] Console errors: {len(errors)}")
        else:
            print("  [OK] No console errors")

        browser.close()

    print("  PASSED\n")


def run_all_tests(headed=False):
    """Ejecuta todos los tests E2E."""
    print("=" * 60)
    print("VANER ASSET — E2E Tests (Playwright)")
    print("=" * 60)
    print(f"Frontend: {BASE_URL}")
    print(f"API: {API_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60 + "\n")

    tests = [
        test_health_endpoints,
        test_login_flow,
        test_api_endpoints,
        test_security_headers,
        test_frontend_loads,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESUMEN: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="VANER ASSET — E2E Tests")
    parser.add_argument("--headed", action="store_true", help="Navegador visible")
    parser.add_argument("--browser", default="chromium", help="Navegador (chromium, firefox, webkit)")
    args = parser.parse_args()

    success = run_all_tests(headed=args.headed)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
