# ============================================================
# BI EJECUTIVO SERVICE
# Archivo: backend/app/services/bi_service.py
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento
from app.models.tecnico import Tecnico


class BIService:

    # ========================================================
    # KPI GENERALES
    # ========================================================

    @staticmethod
    def obtener_kpis_generales(db: Session):

        return {

            "total_empresas":
                db.query(
                    func.count(Empresa.id)
                ).scalar() or 0,

            "total_sedes":
                db.query(
                    func.count(Sede.id)
                ).scalar() or 0,

            "total_equipos":
                db.query(
                    func.count(Equipo.id)
                ).scalar() or 0,

            "total_mantenimientos":
                db.query(
                    func.count(Mantenimiento.id)
                ).scalar() or 0,

            "total_usuarios":
                db.query(
                    func.count(Usuario.id)
                ).scalar() or 0,
        }

    # ========================================================
    # MANTENIMIENTOS POR ESTADO
    # ========================================================

    @staticmethod
    def mantenimientos_por_estado(db: Session):

        resultados = (
            db.query(
                Mantenimiento.estado,
                func.count(Mantenimiento.id)
            )
            .group_by(Mantenimiento.estado)
            .all()
        )

        return [
            {
                "estado": r[0],
                "total": r[1]
            }
            for r in resultados
        ]

    # ========================================================
    # EQUIPOS POR EMPRESA
    # ========================================================

    @staticmethod
    def equipos_por_empresa(db: Session):

        resultados = (
            db.query(
                Empresa.nombre,
                func.count(Equipo.id)
            )
            .outerjoin(
                Equipo,
                Equipo.empresa_id == Empresa.id
            )
            .group_by(Empresa.nombre)
            .all()
        )

        return [
            {
                "empresa": r[0],
                "equipos": r[1]
            }
            for r in resultados
        ]

    # ========================================================
    # COSTOS POR EMPRESA
    # ========================================================

    @staticmethod
    def costos_por_empresa(db: Session):

        resultados = (
            db.query(
                Empresa.nombre,
                func.coalesce(
                    func.sum(Mantenimiento.costo),
                    0
                )
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.empresa_id == Empresa.id
            )
            .group_by(Empresa.nombre)
            .all()
        )

        return [
            {
                "empresa": r[0],
                "costo_total": float(r[1])
            }
            for r in resultados
        ]

    # ========================================================
    # PRODUCTIVIDAD TÉCNICOS
    # ========================================================

    @staticmethod
    def tecnicos_productivos(db: Session):

        resultados = (
            db.query(
                Tecnico.nombre,
                func.count(Mantenimiento.id)
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.tecnico_id == Tecnico.id
            )
            .group_by(Tecnico.nombre)
            .order_by(
                func.count(Mantenimiento.id).desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "tecnico": r[0],
                "mantenimientos": r[1]
            }
            for r in resultados
        ]

    # ========================================================
    # EQUIPOS CRÍTICOS
    # ========================================================

    @staticmethod
    def equipos_criticos(db: Session):

        resultados = (
            db.query(
                Equipo.nombre,
                Empresa.nombre,
                func.count(Mantenimiento.id)
            )
            .join(
                Empresa,
                Equipo.empresa_id == Empresa.id
            )
            .outerjoin(
                Mantenimiento,
                Mantenimiento.equipo_id == Equipo.id
            )
            .group_by(
                Equipo.nombre,
                Empresa.nombre
            )
            .order_by(
                func.count(Mantenimiento.id).desc()
            )
            .limit(10)
            .all()
        )

        return [
            {
                "equipo": r[0],
                "empresa": r[1],
                "mantenimientos": r[2]
            }
            for r in resultados
        ]