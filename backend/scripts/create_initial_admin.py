import argparse
import getpass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the first SGAHolding administrator.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    password = getpass.getpass("Administrator password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation or len(password) < 12:
        print("Passwords must match and contain at least 12 characters.", file=sys.stderr)
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
