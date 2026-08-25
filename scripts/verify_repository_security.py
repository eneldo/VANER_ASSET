import re
import subprocess
from pathlib import Path


repository_files = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
    text=True,
    encoding="utf-8",
).splitlines()
forbidden_env = [
    path
    for path in repository_files
    if Path(path).is_file()
    and Path(path).name.startswith(".env")
    and path != ".env.example"
]
if forbidden_env:
    raise SystemExit("Archivos de entorno versionados: " + ", ".join(forbidden_env))

patterns = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
}
failures = []
for filename in repository_files:
    path = Path(filename)
    if not path.is_file() or path.suffix.lower() in {
        ".png",
        ".jpg",
        ".pdf",
        ".xlsx",
        ".docx",
    }:
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for name, pattern in patterns.items():
        if pattern.search(content):
            failures.append(f"{filename}: {name}")

legacy_auth_router = Path("backend/app/routers/cliente_seguro.py")
security_module = Path("backend/app/security.py")
if legacy_auth_router.exists():
    failures.append(f"Router de autenticación heredado presente: {legacy_auth_router}")
if security_module.exists():
    security_source = security_module.read_text(encoding="utf-8")
    if "def get_current_user" in security_source or "OAuth2PasswordBearer" in security_source:
        failures.append("backend/app/security.py conserva autenticación HTTP heredada")

if failures:
    raise SystemExit("Controles de seguridad incumplidos:\n" + "\n".join(failures))

print("Repositorio sin archivos .env, secretos ni autenticación heredada.")
