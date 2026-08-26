import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password, utc_now
from app.services.password_policy import password_policy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the first VANER ASSET administrator.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    password = getpass.getpass("Administrator password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match.", file=sys.stderr)
        return 2

    temp_user = Usuario(
        username=args.username.strip(),
        email=args.email.strip().lower(),
        nombre_completo=args.name.strip(),
    )
    validation = password_policy.validate(password, usuario=temp_user)
    if not validation.valid:
        for error in validation.errors:
            print(f"Password policy error: {error}", file=sys.stderr)
        return 2

    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.rol == "ADMIN").first():
            print("An administrator already exists.", file=sys.stderr)
            return 1

        username = args.username.strip()
        email = args.email.strip().lower()
        duplicate = db.query(Usuario).filter(
            (Usuario.username == username) | (Usuario.email == email)
        ).first()
        if duplicate:
            print("The username or email is already registered.", file=sys.stderr)
            return 1

        admin = Usuario(
            nombre_completo=args.name.strip(),
            username=username,
            email=email,
            password_hash=hash_password(password),
            rol="ADMIN",
            empresa_id=None,
            activo=True,
            password_changed_at=utc_now(),
        )
        db.add(admin)
        db.commit()
        print(f"Administrator created successfully: {admin.username}")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
