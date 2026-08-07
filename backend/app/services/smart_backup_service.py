# ============================================================
# SERVICIO: Backups Inteligentes SaaS PRO
# Archivo: backend/app/services/smart_backup_service.py
# Fase 34.2.2
# ============================================================

import os
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.models.backup_historial import BackupHistorial
from app.config import settings

# Carpeta persistente recomendada. En Docker/Dokploy puede sobrescribirse con BACKUP_DIR.
BACKUP_DIR = Path(os.getenv("BACKUP_DIR") or "app/backups").resolve()
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Ruta correcta para SGA_SaaS en Docker: /app/app/uploads.
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR") or "app/uploads").resolve()


class SmartBackupService:
    """Motor central para generar, listar, limpiar y descargar backups."""

    def __init__(self, db: Session):
        self.db = db

    def _crear_registro(self, tipo: str, incluir_db: bool, incluir_uploads: bool, incluir_codigo: bool, creado_por: Optional[str]):
        registro = BackupHistorial(
            tipo=tipo.upper(),
            estado="EN_PROCESO",
            mensaje="Backup iniciado",
            incluye_db=incluir_db,
            incluye_uploads=incluir_uploads,
            incluye_codigo=incluir_codigo,
            creado_por=creado_por or "sistema",
            metadata_json={},
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def ejecutar_backup(self, tipo="MANUAL", incluir_db=True, incluir_uploads=True, incluir_codigo=False, creado_por="admin") -> BackupHistorial:
        registro = self._crear_registro(tipo, incluir_db, incluir_uploads, incluir_codigo, creado_por)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        work_dir = BACKUP_DIR / f"tmp_backup_{timestamp}"
        zip_name = f"sga_backup_{timestamp}.zip"
        zip_path = BACKUP_DIR / zip_name
        work_dir.mkdir(parents=True, exist_ok=True)

        try:
            metadata = {}

            if incluir_db:
                sql_file = work_dir / f"postgres_sga_{timestamp}.sql"
                self._dump_postgres(sql_file)
                metadata["db_sql"] = sql_file.name

            if incluir_uploads:
                uploads_zip = work_dir / f"uploads_{timestamp}.zip"
                self._zip_folder(UPLOAD_DIR, uploads_zip)
                metadata["uploads_zip"] = uploads_zip.name

            if incluir_codigo:
                code_zip = work_dir / f"codigo_backend_{timestamp}.zip"
                self._zip_folder(Path("/app"), code_zip, exclude_names={".venv", "__pycache__", "node_modules", "backups"})
                metadata["codigo_zip"] = code_zip.name

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in work_dir.iterdir():
                    if item.is_file():
                        zf.write(item, arcname=item.name)

            remote_key = self._upload_remote_backup(zip_path)
            if remote_key:
                metadata["remote_key"] = remote_key

            registro.estado = "EXITOSO"
            registro.nombre_archivo = zip_name
            registro.ruta_archivo = str(zip_path)
            registro.tamano_bytes = zip_path.stat().st_size if zip_path.exists() else 0
            registro.mensaje = "Backup generado correctamente"
            registro.finalizado_en = datetime.now(timezone.utc)
            registro.metadata_json = metadata
            self.db.commit()
            self.db.refresh(registro)
            return registro

        except Exception as exc:
            registro.estado = "ERROR"
            registro.mensaje = f"Error generando backup: {exc}"
            registro.finalizado_en = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(registro)
            raise HTTPException(status_code=500, detail=registro.mensaje)
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    def _upload_remote_backup(self, backup_path: Path) -> str | None:
        if not settings.S3_BACKUP_ENABLED:
            return None

        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=settings.S3_BACKUP_ENDPOINT_URL,
            region_name=settings.S3_BACKUP_REGION,
            aws_access_key_id=settings.S3_BACKUP_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_BACKUP_SECRET_ACCESS_KEY,
        )
        prefix = settings.S3_BACKUP_PREFIX.strip("/")
        remote_key = f"{prefix}/{backup_path.name}" if prefix else backup_path.name
        client.upload_file(
            str(backup_path),
            settings.S3_BACKUP_BUCKET,
            remote_key,
            ExtraArgs={"ServerSideEncryption": "AES256"},
        )
        return remote_key

    def _dump_postgres(self, destino: Path):
        database_url = settings.BACKUP_DATABASE_URL
        if not database_url and settings.APP_ENV.lower() != "production":
            database_url = settings.DATABASE_URL
        if not database_url:
            raise RuntimeError("BACKUP_DATABASE_URL es obligatoria para generar backups")

        env = os.environ.copy()

        if database_url.startswith("postgres"):
            url = make_url(database_url)
            pg_user = url.username
            pg_db = url.database
            pg_host = url.host
            pg_port = str(url.port or 5432)
            pg_password = url.password
        else:
            pg_user = os.getenv("POSTGRES_USER")
            pg_db = os.getenv("POSTGRES_DB")
            pg_host = os.getenv("POSTGRES_HOST")
            pg_port = os.getenv("POSTGRES_PORT") or "5432"
            pg_password = os.getenv("POSTGRES_PASSWORD")

        if not all((pg_user, pg_db, pg_host, pg_password)):
            raise RuntimeError("Configuración PostgreSQL incompleta para generar el backup")

        env["PGPASSWORD"] = pg_password
        cmd = [
            "pg_dump",
            "-h", pg_host,
            "-p", pg_port,
            "-U", pg_user,
            "-d", pg_db,
        ]

        with destino.open("wb") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode("utf-8", errors="ignore") or "pg_dump falló")

    def _zip_folder(self, carpeta: Path, destino: Path, exclude_names=None):
        exclude_names = exclude_names or set()
        if not carpeta.exists():
            with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("README.txt", f"Carpeta no encontrada: {carpeta}")
            return

        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in carpeta.rglob("*"):
                if any(part in exclude_names for part in path.parts):
                    continue
                if path.is_file():
                    zf.write(path, arcname=str(path.relative_to(carpeta)))

    def listar(self, limit: int = 50):
        return self.db.query(BackupHistorial).order_by(BackupHistorial.iniciado_en.desc()).limit(limit).all()

    def obtener(self, backup_id: UUID) -> BackupHistorial:
        obj = self.db.query(BackupHistorial).filter(BackupHistorial.id == backup_id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Backup no encontrado")
        return obj

    def limpiar_antiguos(self, retencion_dias: int = 15) -> int:
        limite = datetime.now(timezone.utc) - timedelta(days=retencion_dias)
        antiguos = self.db.query(BackupHistorial).filter(BackupHistorial.iniciado_en < limite).all()
        eliminados = 0
        for item in antiguos:
            if item.ruta_archivo:
                try:
                    Path(item.ruta_archivo).unlink(missing_ok=True)
                except Exception:
                    pass
            self.db.delete(item)
            eliminados += 1
        self.db.commit()
        return eliminados

    def status(self):
        backups = self.listar(1000)
        total_bytes = sum(b.tamano_bytes or 0 for b in backups)
        ultimo = backups[0] if backups else None
        return {
            "ok": True,
            "backups_dir": str(BACKUP_DIR),
            "total_backups": len(backups),
            "total_bytes": total_bytes,
            "ultimo_backup": ultimo,
            "mensaje": "Servicio de backups inteligente operativo",
        }
