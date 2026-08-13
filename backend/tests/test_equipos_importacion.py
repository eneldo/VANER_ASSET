import unittest
from io import BytesIO
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.categoria import Categoria
from app.models.empresa import Empresa
from app.models.equipo import Equipo
from app.models.sede import Sede
from app.routers.equipos import (
    importar_equipos,
    normalizar_celda_importacion,
    validar_numero_inventario,
)


class EquiposImportacionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(
            self.engine,
            tables=[
                Empresa.__table__,
                Sede.__table__,
                Categoria.__table__,
                Equipo.__table__,
            ],
        )
        Session = sessionmaker(bind=self.engine)
        self.db = Session()

        self.empresa = Empresa(id=uuid4(), nombre="ESE SALUD YOPAL", activo=True)
        self.sede = Sede(
            id=uuid4(),
            empresa_id=self.empresa.id,
            nombre="Hospital Central",
            activo=True,
        )
        self.categoria = Categoria(
            id=uuid4(),
            code="AIRES_ACONDICIONADOS",
            nombre="Aires Acondicionados",
            activo=True,
        )
        self.db.add_all([self.empresa, self.sede, self.categoria])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    @staticmethod
    def archivo_csv(filas):
        encabezado = (
            "codigo_inventario,nombre,empresa,sede,categoria,marca,modelo,"
            "serie,ubicacion,estado,criticidad,inventario\n"
        )
        contenido = encabezado + "\n".join(filas) + "\n"
        return UploadFile(
            filename="inventario.csv",
            file=BytesIO(contenido.encode("utf-8")),
        )

    async def test_importaciones_sucesivas_omiten_repetidos_y_crean_nuevos(self):
        primera = await importar_equipos(
            self.archivo_csv([
                "EQ-001,Mini Split 1,ESE SALUD YOPAL,Hospital Central,"
                "Aires Acondicionados,York,M1,S1,Consultorio,OPERATIVO,BAJA,INV-001",
            ]),
            self.db,
        )
        segunda = await importar_equipos(
            self.archivo_csv([
                "EQ-001,Mini Split repetido,ESE SALUD YOPAL,Hospital Central,"
                "Aires Acondicionados,York,M1,S1,Consultorio,OPERATIVO,BAJA,INV-099",
                "EQ-002,Mini Split 2,ESE SALUD YOPAL,Hospital Central,"
                "Aires Acondicionados,York,M2,S2,Oficina,OPERATIVO,BAJA,INV-002",
            ]),
            self.db,
        )
        tercera = await importar_equipos(
            self.archivo_csv([
                "EQ-003,Mini Split 3,ESE SALUD YOPAL,Hospital Central,"
                "Aires Acondicionados,York,M3,S3,Archivo,OPERATIVO,BAJA,INV-003",
            ]),
            self.db,
        )

        self.assertEqual(primera, {"creados": 1, "omitidos": 0, "errores": []})
        self.assertEqual(segunda["creados"], 1)
        self.assertEqual(segunda["omitidos"], 1)
        self.assertEqual(segunda["errores"][0]["fila"], 2)
        self.assertIn("código de inventario está registrado", segunda["errores"][0]["error"])
        self.assertEqual(tercera, {"creados": 1, "omitidos": 0, "errores": []})
        self.assertEqual(self.db.query(Equipo).count(), 3)
        self.assertEqual(
            {equipo.codigo_id for equipo in self.db.query(Equipo).all()},
            {"EQ-001", "EQ-002", "EQ-003"},
        )

    def test_normaliza_codigos_numericos_de_excel(self):
        self.assertEqual(normalizar_celda_importacion(12147.0), "12147")
        self.assertIsNone(normalizar_celda_importacion(float("nan")))
        self.assertEqual(normalizar_celda_importacion("  EQ-001  "), "EQ-001")

    def test_formulario_manual_detecta_inventario_importado_como_codigo(self):
        self.db.add(Equipo(
            nombre="Equipo importado",
            empresa_id=self.empresa.id,
            sede_id=self.sede.id,
            categoria_id=self.categoria.id,
            codigo_id="17774",
            inventario=None,
            estado="OPERATIVO",
            criticidad="BAJA",
            activo=True,
        ))
        self.db.commit()

        with self.assertRaises(HTTPException) as context:
            validar_numero_inventario(self.db, " 17774 ")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Equipo ya existe", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
