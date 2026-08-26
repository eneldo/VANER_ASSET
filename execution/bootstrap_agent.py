#!/usr/bin/env python3
"""
bootstrap_agent.py

Inicializa un workspace preparado para agentes de IA persistentes.

Compatible conceptualmente con:

- OpenAI Codex / ChatGPT
- Claude Code
- Gemini CLI
- otros agentes que lean Markdown del proyecto

Crea:

.agent/
memory/
directives/
execution/
decisions/
errors/
architecture/
docs/
tests/
logs/
.tmp/

y prepara:

.agent/MASTER_AGENT.md
AGENTS.md
CLAUDE.md
GEMINI.md
.env.example
.gitignore

Uso:

    python execution/bootstrap_agent.py

Vista previa:

    python execution/bootstrap_agent.py --dry-run

Forzar regeneración únicamente de plantillas vacías:

    python execution/bootstrap_agent.py --force
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


DIRECTORIES = [
    ".agent",
    "memory",
    "memory/history",
    "directives",
    "execution",
    "decisions",
    "errors",
    "architecture",
    "docs",
    "tests",
    "logs",
    ".tmp",
]


MASTER_TEMPLATE = """# AGENTE MAESTRO DEL PROYECTO

> FUENTE CANÓNICA DE INSTRUCCIONES.
>
> Este archivo controla AGENTS.md, CLAUDE.md y GEMINI.md.
>
> No edites los archivos derivados directamente.
> Modifica este archivo y después ejecuta:
>
>     python execution/sync_agent_files.py


# MISIÓN

Operar como agente de ingeniería persistente del proyecto.

El agente debe:

1. comprender antes de modificar;
2. consultar memoria antes de resolver problemas ya conocidos;
3. reutilizar herramientas existentes;
4. preferir ejecución determinista;
5. validar cambios;
6. aprender de errores no triviales;
7. convertir conocimiento repetitivo en automatización;
8. mantener documentación y memoria consistentes.


# INICIO OBLIGATORIO DE SESIÓN

Antes de una tarea importante:

1. Leer este archivo.
2. Leer `memory/project_context.md`.
3. Leer `memory/session_summary.md`.
4. Consultar aprendizajes recientes.
5. Consultar `memory/known_issues.md` si existe un problema.
6. Revisar directivas relevantes.
7. Inspeccionar código y configuración real.
8. Ejecutar la tarea.


# ARQUITECTURA DE 3 CAPAS

## Capa 1 — Directivas

Ubicación:

    directives/

Contienen procedimientos y SOPs.

Definen QUÉ hacer.


## Capa 2 — Orquestación

Responsabilidad del agente.

Debe:

- interpretar intención;
- seleccionar directivas;
- seleccionar herramientas;
- manejar errores;
- validar;
- documentar aprendizaje.


## Capa 3 — Ejecución

Ubicación:

    execution/

Contiene scripts deterministas.

Preferir scripts reutilizables a repetir manualmente procesos complejos.


# MEMORIA PERSISTENTE

Ubicación:

    memory/

Archivos principales:

    project_context.md
    learnings.md
    known_issues.md
    solutions.md
    patterns.md
    environment.md
    user_preferences.md
    session_summary.md

No llenar la memoria con información trivial.


# APRENDIZAJE CONTINUO

Registrar un aprendizaje únicamente si surge conocimiento reutilizable.

Formato:

    - **YYYY-MM-DD — Tema:**
      **Contexto:** ...
      **Aprendizaje:** ...
      **Aplicación futura:** ...


# CICLO DE AUTOCORRECCIÓN

Cuando algo falle:

1. leer error;
2. revisar logs;
3. identificar causa raíz;
4. aplicar corrección mínima;
5. volver a probar;
6. ejecutar regresiones relevantes;
7. registrar aprendizaje si corresponde;
8. automatizar prevención cuando resulte útil.


# CONOCIMIENTO PROMOVIDO

El conocimiento debe evolucionar:

    Error
      ↓
    Aprendizaje
      ↓
    Patrón
      ↓
    Directiva
      ↓
    Script
      ↓
    Test

El objetivo es no resolver manualmente el mismo problema indefinidamente.


# TESTS COMO MEMORIA

Cuando se corrija un bug importante:

considerar crear un test que reproduzca el problema.

Ideal:

    bug
    ↓
    test falla
    ↓
    corrección
    ↓
    test pasa


# SEGURIDAD

Nunca guardar secretos en Markdown.

No almacenar:

- passwords;
- API keys;
- tokens;
- claves privadas;
- cookies;
- credenciales.

Utilizar `.env` y mantener `.env.example` sin valores sensibles.


# ARCHIVOS TEMPORALES

Utilizar:

    .tmp/

para artefactos regenerables.

No versionar `.tmp/`.


# GIT

Antes de cambios grandes:

    git status

Después:

    git diff

No sobrescribir trabajo existente del usuario.

No ejecutar comandos destructivos sin autorización explícita.


# VALIDACIÓN

Antes de declarar una tarea terminada:

- comprobar sintaxis;
- ejecutar tests relevantes;
- ejecutar build si corresponde;
- revisar regresiones;
- actualizar documentación;
- registrar aprendizaje relevante.


# FIN DE SESIÓN

Después de trabajo significativo:

1. actualizar `memory/session_summary.md`;
2. actualizar contexto si cambió el proyecto;
3. registrar aprendizajes útiles;
4. registrar errores reutilizables;
5. actualizar ADR si hubo decisiones arquitectónicas;
6. sincronizar archivos del agente ejecutando:

       python execution/sync_agent_files.py


# PRINCIPIOS

LEER ANTES DE CAMBIAR.

COMPRENDER ANTES DE REESCRIBIR.

REUTILIZAR ANTES DE CREAR.

PROBAR ANTES DE DECLARAR ÉXITO.

CORREGIR CAUSAS, NO SOLO SÍNTOMAS.

AUTOMATIZAR LO REPETITIVO.

CONVERTIR BUGS EN TESTS.

CONVERTIR EXPERIENCIA EN MEMORIA.

NO EXPONER SECRETOS.

NO INVENTAR RESULTADOS.

NO REPETIR ERRORES EVITABLES.
"""


FILES = {

    "memory/README.md": """# Memoria Persistente

Esta carpeta contiene conocimiento persistente del proyecto.

No utilizarla como log exhaustivo.

El objetivo es preservar conocimiento útil entre sesiones de diferentes agentes.
""",

    "memory/project_context.md": """# Contexto del Proyecto

## Objetivo

Pendiente de analizar.

## Estado actual

Pendiente de analizar.

## Arquitectura

Pendiente de analizar.

## Backend

Pendiente de analizar.

## Frontend

Pendiente de analizar.

## Base de datos

Pendiente de analizar.

## Infraestructura

Pendiente de analizar.

## Servicios externos

Pendiente de analizar.

## Seguridad

Pendiente de analizar.

## Funcionalidades terminadas

Pendiente.

## Funcionalidades pendientes

Pendiente.

## Riesgos conocidos

Pendiente.
""",

    "memory/learnings.md": """# Aprendizajes del Agente

Los aprendizajes más recientes deben agregarse arriba.

Formato:

- **YYYY-MM-DD — Tema:**
  **Contexto:** qué ocurrió.
  **Aprendizaje:** qué se descubrió.
  **Aplicación futura:** cómo aplicar este conocimiento.

---

<!-- Nuevos aprendizajes debajo de esta línea -->

""",

    "memory/conventions.md": """# Convenciones del Proyecto

Registrar aquí convenciones estables descubiertas en el proyecto.
""",

    "memory/user_preferences.md": """# Preferencias del Proyecto

Registrar únicamente preferencias técnicas y operativas relevantes y estables.
""",

    "memory/known_issues.md": """# Problemas Conocidos

Registrar problemas importantes que puedan reaparecer.

## Formato

### ISSUE-XXXX — Título

**Estado:** OPEN / MITIGATED / RESOLVED

**Síntoma:**

**Causa:**

**Solución o mitigación:**

**Prevención:**
""",

    "memory/solutions.md": """# Soluciones Verificadas

Soluciones técnicas reutilizables comprobadas durante el desarrollo.
""",

    "memory/environment.md": """# Entorno

## Sistema operativo

Pendiente.

## Python

Pendiente.

## Node.js

Pendiente.

## Docker

Pendiente.

## Base de datos

Pendiente.

## Servicios

Pendiente.

Nunca almacenar secretos en este archivo.
""",

    "memory/dependencies.md": """# Dependencias Importantes

Registrar dependencias críticas, restricciones y compatibilidades relevantes.
""",

    "memory/patterns.md": """# Patrones Reutilizables

Registrar patrones técnicos que hayan demostrado funcionar correctamente.
""",

    "memory/session_summary.md": f"""# Última sesión

Fecha: {date.today().isoformat()}

## Objetivo trabajado

Inicialización del sistema de agente persistente.

## Cambios realizados

Preparación de memoria, directivas y sistema de sincronización.

## Problemas encontrados

Ninguno registrado.

## Estado actual

Workspace preparado para aprendizaje continuo.

## Pendientes

Analizar el proyecto real y completar `memory/project_context.md`.

## Próximo paso recomendado

Ejecutar análisis inicial del repositorio.
""",

    "directives/README.md": """# Directivas

Procedimientos operativos reutilizables del proyecto.

Las directivas describen QUÉ hacer.

La ejecución determinista vive en `execution/`.
""",

    "directives/development.md": """# Desarrollo

## Objetivo

Definir el procedimiento estándar para implementar cambios.

## Procedimiento general

1. comprender requisito;
2. consultar memoria;
3. inspeccionar código;
4. localizar implementación existente;
5. realizar cambio mínimo;
6. validar;
7. ejecutar pruebas;
8. registrar aprendizajes relevantes.
""",

    "directives/debugging.md": """# Depuración

## Procedimiento

1. reproducir el problema;
2. capturar error;
3. leer stack trace;
4. consultar problemas conocidos;
5. identificar causa raíz;
6. aplicar corrección mínima;
7. verificar;
8. crear test de regresión cuando corresponda;
9. registrar aprendizaje reutilizable.
""",

    "directives/testing.md": """# Testing

Utilizar las herramientas de prueba existentes en el proyecto.

No inventar comandos.

Consultar primero archivos como:

- package.json
- pyproject.toml
- Makefile
- README
- scripts existentes
""",

    "directives/deployment.md": """# Deployment

No realizar despliegues destructivos sin verificar:

- configuración;
- variables;
- backups;
- servicios;
- migraciones;
- health checks;
- rollback.
""",

    "directives/security.md": """# Seguridad

Nunca versionar secretos.

Verificar:

- `.env`;
- credenciales;
- permisos;
- dependencias;
- exposición de servicios;
- logs sensibles.
""",

    "decisions/README.md": """# Architecture Decision Records

Formato recomendado:

ADR-0001-nombre.md

Cada ADR debería contener:

- contexto;
- opciones;
- decisión;
- razones;
- consecuencias;
- fecha.
""",

    "errors/README.md": """# Registro de Errores

Utilizar únicamente para problemas importantes o recurrentes.
""",

    "errors/recurring_errors.md": """# Errores Recurrentes
""",

    "errors/resolved_errors.md": """# Errores Resueltos
""",

    "architecture/README.md": """# Arquitectura

Documentación de arquitectura del sistema.
""",

    ".env.example": """# Copiar a .env y completar localmente.

# Ejemplo:
# DATABASE_URL=
# API_KEY=
""",
}


GITIGNORE_ENTRIES = [
    ".env",
    ".env.*",
    "!.env.example",
    ".tmp/",
    "logs/",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    "credentials.json",
    "token.json",
]


def log(message: str) -> None:
    print(message)


def create_directory(path: Path, dry_run: bool) -> None:

    if path.exists():
        log(f"[OK]       {path.relative_to(ROOT)}/")
        return

    log(f"[CREATE]   {path.relative_to(ROOT)}/")

    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)


def create_file(
    path: Path,
    content: str,
    dry_run: bool,
    force: bool = False,
) -> None:

    if path.exists() and not force:
        log(f"[KEEP]     {path.relative_to(ROOT)}")
        return

    action = "[REPLACE]" if path.exists() else "[CREATE]"

    log(f"{action:10} {path.relative_to(ROOT)}")

    if dry_run:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        content,
        encoding="utf-8",
        newline="\n",
    )


def update_gitignore(dry_run: bool) -> None:

    gitignore = ROOT / ".gitignore"

    existing = ""

    if gitignore.exists():
        existing = gitignore.read_text(encoding="utf-8")

    lines = existing.splitlines()

    additions = []

    for entry in GITIGNORE_ENTRIES:
        if entry not in lines:
            additions.append(entry)

    if not additions:
        log("[OK]       .gitignore")
        return

    log(
        "[UPDATE]   .gitignore "
        f"(+{len(additions)} reglas)"
    )

    if dry_run:
        return

    new_content = existing.rstrip()

    if new_content:
        new_content += "\n\n"

    new_content += "# Agent workspace / secrets\n"
    new_content += "\n".join(additions)
    new_content += "\n"

    gitignore.write_text(
        new_content,
        encoding="utf-8",
        newline="\n",
    )


def detect_project() -> None:

    print("\n=== Detección básica del proyecto ===\n")

    detectors = {
        "Python": [
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
        ],
        "Node.js": [
            "package.json",
        ],
        "Docker": [
            "Dockerfile",
            "docker-compose.yml",
            "compose.yml",
            "compose.yaml",
        ],
        "Git": [
            ".git",
        ],
    }

    found_any = False

    for technology, candidates in detectors.items():

        detected = any(
            (ROOT / candidate).exists()
            for candidate in candidates
        )

        if detected:
            print(f"[DETECTED] {technology}")
            found_any = True

    if not found_any:
        print("[INFO] No se detectaron tecnologías mediante reglas básicas.")


def git_status() -> None:

    if not (ROOT / ".git").exists():
        return

    print("\n=== Estado Git ===\n")

    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        output = result.stdout.strip()

        if output:
            print(output)
        else:
            print("Repositorio limpio.")

    except FileNotFoundError:
        print("[WARN] Git no está disponible en PATH.")


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        description="Inicializa workspace de agente persistente."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra cambios sin realizarlos.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Permite reemplazar archivos de plantilla. "
            "Usar con cuidado."
        ),
    )

    return parser.parse_args()


def main() -> None:

    args = parse_args()

    print("\n==============================================")
    print("     AGENT WORKSPACE BOOTSTRAP")
    print("==============================================\n")

    print(f"Proyecto: {ROOT}\n")

    detect_project()

    print("\n=== Directorios ===\n")

    for directory in DIRECTORIES:
        create_directory(
            ROOT / directory,
            args.dry_run,
        )

    print("\n=== Archivos ===\n")

    master = ROOT / ".agent" / "MASTER_AGENT.md"

    create_file(
        master,
        MASTER_TEMPLATE,
        args.dry_run,
        force=False,
    )

    for relative_path, content in FILES.items():
        create_file(
            ROOT / relative_path,
            content,
            args.dry_run,
            force=args.force,
        )

    update_gitignore(args.dry_run)

    if args.dry_run:
        print(
            "\n[DRY-RUN] No se realizaron modificaciones."
        )
        return

    sync_script = ROOT / "execution" / "sync_agent_files.py"

    if sync_script.exists():

        print("\n=== Sincronización ===\n")

        result = subprocess.run(
            [
                sys.executable,
                str(sync_script),
            ],
            cwd=ROOT,
            check=False,
        )

        if result.returncode != 0:
            print(
                "\n[WARN] La sincronización terminó con errores."
            )

    else:
        print(
            "\n[WARN] execution/sync_agent_files.py "
            "todavía no existe."
        )

        print(
            "Créalo y ejecuta:\n\n"
            "    python execution/sync_agent_files.py"
        )

    git_status()

    print("\n==============================================")
    print(" Workspace del agente inicializado")
    print("==============================================")

    print(
        "\nSiguiente paso recomendado:\n\n"
        "    python execution/sync_agent_files.py --check\n"
    )


if __name__ == "__main__":
    main()