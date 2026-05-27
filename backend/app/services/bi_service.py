# ============================================================
# BI EJECUTIVO SERVICE
# ============================================================

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.equipo import Equipo
from app.models.usuario import Usuario
from app.models.mantenimiento import Mantenimiento


class BIService:

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