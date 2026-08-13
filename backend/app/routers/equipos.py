# =========================================================
# ROUTER EQUIPOS
# CRUD de equipos básicos - PASO 1 hoja de vida
# =========================================================

from datetime import datetime
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.equipo import Equipo
from app.models.empresa import Empresa
from app.models.sede import Sede
from app.models.categoria import Categoria, CATEGORIA_CODES
from app.schemas.equipo import EquipoCreate, EquipoUpdate, EquipoOut
from app.core.auth_dependencies import require_roles


router = APIRouter(
    prefix="/equipos",
    tags=["Equipos"],
    dependencies=[Depends(require_roles("ADMIN"))],
)


# Estados permitidos del equipo
ESTADOS_EQUIPO = [
    "OPERATIVO",
    "EN_MANTENIMIENTO",
    "FUERA_DE_SERVICIO",
    "BAJA"
]

# Criticidades permitidas del equipo
CRITICIDADES_EQUIPO = [
    "BAJA",
    "MEDIA",
    "ALTA",
    "CRITICA"
]


def normalizar_numero_inventario(value):
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    numero = str(value).strip()
    return numero or None


def validar_numero_inventario(
    db: Session,
    value,
    *,
    excluir_equipo_id: UUID | None = None,
):
    numero = normalizar_numero_inventario(value)
    if not numero:
        return None

    filtros = [func.lower(func.trim(Equipo.inventario)) == numero.lower()]
    if excluir_equipo_id:
        filtros.append(Equipo.id != excluir_equipo_id)

    existente = db.query(Equipo).filter(*filtros).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Equipo ya existe: el número de inventario está registrado",
        )

    return numero

COLUMNAS_EXPORTACION = [
    "codigo_inventario",
    "nombre",
    "empresa",
    "sede",
    "categoria",
    "marca",
    "modelo",
    "serie",
    "ubicacion",
    "estado",
    "criticidad",
    "invima",
    "inventario",
    "activo",
    "fecha_creacion",
]


def _valor_excel(value, fallback="SIN DATO"):
    """Convierte valores a texto seguro y evita formulas inyectadas en Excel."""
    if value is None or str(value).strip() == "":
        return fallback
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")

    text = str(value).strip()
    return f"'{text}" if text.startswith(("=", "+", "-", "@")) else text


def crear_excel_inventario(filas):
    """Genera un libro compatible con importacion y datos de respaldo."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Inventario"

    header_fill = PatternFill("solid", fgColor="17365D")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9E2F3")

    for column_index, column_name in enumerate(COLUMNAS_EXPORTACION, start=1):
        cell = sheet.cell(row=1, column=column_index, value=column_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(bottom=thin)

    for row_index, fila in enumerate(filas, start=2):
        for column_index, column_name in enumerate(COLUMNAS_EXPORTACION, start=1):
            fallback = (
                f"SIN-INVENTARIO-{row_index:04d}"
                if column_name == "codigo_inventario"
                else "SIN DATO"
            )
            sheet.cell(
                row=row_index,
                column=column_index,
                value=_valor_excel(fila.get(column_name), fallback),
            ).alignment = Alignment(vertical="top")

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = (
        f"A1:{get_column_letter(len(COLUMNAS_EXPORTACION))}{max(sheet.max_row, 1)}"
    )
    sheet.row_dimensions[1].height = 28

    widths = [22, 24, 26, 28, 34, 18, 22, 20, 36, 24, 16, 18, 20, 12, 22]
    for column_index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(column_index)].width = width

    estado_validation = DataValidation(
        type="list",
        formula1='"OPERATIVO,EN_MANTENIMIENTO,FUERA_DE_SERVICIO,BAJA"',
        allow_blank=False,
    )
    criticidad_validation = DataValidation(
        type="list",
        formula1='"BAJA,MEDIA,ALTA,CRITICA"',
        allow_blank=False,
    )
    sheet.add_data_validation(estado_validation)
    sheet.add_data_validation(criticidad_validation)
    estado_validation.add(f"J2:J{max(sheet.max_row, 2)}")
    criticidad_validation.add(f"K2:K{max(sheet.max_row, 2)}")

    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def validar_relaciones_equipo(data, db: Session):
    """
    Valida que empresa, sede y categoría existan.
    También valida que la sede pertenezca a la empresa.
    """

    # Validar empresa
    empresa = db.query(Empresa).filter(Empresa.id == data.empresa_id).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa asociada no existe"
        )

    # Validar sede
    sede = db.query(Sede).filter(Sede.id == data.sede_id).first()

    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La sede asociada no existe"
        )

    # Validar que la sede pertenezca a la empresa seleccionada
    if sede.empresa_id != data.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sede no pertenece a la empresa seleccionada"
        )

    # Validar categoría si se envió
    if data.categoria_id:
        categoria = db.query(Categoria).filter(
            Categoria.id == data.categoria_id
        ).first()

        if not categoria or not categoria.activo or categoria.code not in CATEGORIA_CODES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría asociada no existe"
            )


def validar_estado_y_criticidad(estado: str, criticidad: str):
    """
    Valida valores permitidos de estado y criticidad.
    """

    if estado not in ESTADOS_EQUIPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado no permitido. Use uno de: {ESTADOS_EQUIPO}"
        )

    if criticidad not in CRITICIDADES_EQUIPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Criticidad no permitida. Use una de: {CRITICIDADES_EQUIPO}"
        )


@router.post("/", response_model=EquipoOut)
def crear_equipo(data: EquipoCreate, db: Session = Depends(get_db)):
    """
    Crea un equipo con datos básicos.
    Este es el PASO 1 del flujo de hoja de vida en dos pasos.
    """

    # Validar relaciones empresa/sede/categoría
    validar_relaciones_equipo(data, db)

    # Validar estado y criticidad
    validar_estado_y_criticidad(data.estado, data.criticidad)

    # Validar código único si se envía
    if data.codigo_id:
        existente = db.query(Equipo).filter(
            Equipo.codigo_id == data.codigo_id
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un equipo con ese Código ID"
            )

    datos = data.model_dump()
    datos["inventario"] = validar_numero_inventario(db, datos.get("inventario"))
    nuevo_equipo = Equipo(**datos)

    db.add(nuevo_equipo)
    db.commit()
    db.refresh(nuevo_equipo)

    return nuevo_equipo


@router.get("/", response_model=list[EquipoOut])
def listar_equipos(db: Session = Depends(get_db)):
    """
    Lista todos los equipos registrados.
    """

    equipos = db.query(Equipo).order_by(Equipo.created_at.desc()).all()
    return equipos


@router.get("/empresa/{empresa_id}", response_model=list[EquipoOut])
def listar_equipos_por_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    """
    Lista equipos filtrados por empresa.
    Esta ruta será usada por el portal EMPRESA.
    """

    equipos = db.query(Equipo).filter(
        Equipo.empresa_id == empresa_id
    ).order_by(Equipo.created_at.desc()).all()

    return equipos


@router.get("/sede/{sede_id}", response_model=list[EquipoOut])
def listar_equipos_por_sede(sede_id: UUID, db: Session = Depends(get_db)):
    """
    Lista equipos filtrados por sede.
    """

    equipos = db.query(Equipo).filter(
        Equipo.sede_id == sede_id
    ).order_by(Equipo.created_at.desc()).all()

    return equipos


@router.get("/exportar")
def exportar_inventario_equipos(db: Session = Depends(get_db)):
    """Descarga el inventario completo en un archivo Excel."""
    registros = (
        db.query(
            Equipo,
            Empresa.nombre.label("empresa_nombre"),
            Sede.nombre.label("sede_nombre"),
            Categoria.nombre.label("categoria_nombre"),
        )
        .outerjoin(Empresa, Empresa.id == Equipo.empresa_id)
        .outerjoin(Sede, Sede.id == Equipo.sede_id)
        .outerjoin(Categoria, Categoria.id == Equipo.categoria_id)
        .order_by(Empresa.nombre, Sede.nombre, Equipo.nombre)
        .all()
    )

    filas = [
        {
            "codigo_inventario": equipo.codigo_id,
            "nombre": equipo.nombre,
            "empresa": empresa_nombre,
            "sede": sede_nombre,
            "categoria": categoria_nombre,
            "marca": equipo.marca,
            "modelo": equipo.modelo,
            "serie": equipo.serie,
            "ubicacion": equipo.ubicacion,
            "estado": equipo.estado,
            "criticidad": equipo.criticidad,
            "invima": equipo.invima,
            "inventario": equipo.inventario,
            "activo": "SI" if equipo.activo else "NO",
            "fecha_creacion": equipo.created_at,
        }
        for equipo, empresa_nombre, sede_nombre, categoria_nombre in registros
    ]

    filename = f"inventario_equipos_sga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        crear_excel_inventario(filas),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{equipo_id}", response_model=EquipoOut)
def obtener_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Obtiene un equipo por ID.
    """

    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    return equipo


@router.put("/{equipo_id}", response_model=EquipoOut)
def actualizar_equipo(
    equipo_id: UUID,
    data: EquipoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza datos básicos de un equipo.
    """

    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    datos = data.model_dump(exclude_unset=True)

    if "inventario" in datos:
        inventario_actual = normalizar_numero_inventario(equipo.inventario)
        inventario_nuevo = normalizar_numero_inventario(datos["inventario"])
        datos["inventario"] = (
            inventario_nuevo
            if inventario_nuevo == inventario_actual
            else validar_numero_inventario(
                db,
                inventario_nuevo,
                excluir_equipo_id=equipo_id,
            )
        )

    # Validar código único si cambia
    if "codigo_id" in datos and datos["codigo_id"]:
        existente = db.query(Equipo).filter(
            Equipo.codigo_id == datos["codigo_id"],
            Equipo.id != equipo_id
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro equipo con ese Código ID"
            )

    # Validar estado si se envía
    if "estado" in datos and datos["estado"] not in ESTADOS_EQUIPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado no permitido. Use uno de: {ESTADOS_EQUIPO}"
        )

    # Validar criticidad si se envía
    if "criticidad" in datos and datos["criticidad"] not in CRITICIDADES_EQUIPO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Criticidad no permitida. Use una de: {CRITICIDADES_EQUIPO}"
        )

    # Si se cambia empresa/sede, validar consistencia
    empresa_id_final = datos.get("empresa_id", equipo.empresa_id)
    sede_id_final = datos.get("sede_id", equipo.sede_id)

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id_final).first()

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La empresa asociada no existe"
        )

    sede = db.query(Sede).filter(Sede.id == sede_id_final).first()

    if not sede:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La sede asociada no existe"
        )

    if sede.empresa_id != empresa_id_final:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La sede no pertenece a la empresa seleccionada"
        )

    # Validar categoría si se cambia
    if "categoria_id" in datos and datos["categoria_id"]:
        categoria = db.query(Categoria).filter(
            Categoria.id == datos["categoria_id"]
        ).first()

        if not categoria or not categoria.activo or categoria.code not in CATEGORIA_CODES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La categoría asociada no existe"
            )

    # Aplicar cambios
    for campo, valor in datos.items():
        setattr(equipo, campo, valor)

    db.commit()
    db.refresh(equipo)

    return equipo


@router.delete("/{equipo_id}")
def eliminar_equipo(equipo_id: UUID, db: Session = Depends(get_db)):
    """
    Elimina un equipo.
    Nota: más adelante podemos cambiar a eliminación lógica activo=False.
    """

    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()

    if not equipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado"
        )

    db.delete(equipo)
    db.commit()

    return {"message": "Equipo eliminado correctamente"}

# =========================================================
# IMPORTAR INVENTARIO DESDE EXCEL / CSV
# =========================================================


@router.post("/importar")
async def importar_equipos(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Importa equipos desde archivo Excel o CSV.
    """

    try:
        contenido = await archivo.read()

        # Detectar tipo de archivo
        if archivo.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contenido))
        else:
            df = pd.read_excel(BytesIO(contenido))

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error leyendo archivo: {str(e)}"
        )

    # Columnas requeridas
    columnas = [
        "codigo_inventario",
        "nombre",
        "empresa",
        "sede",
        "categoria",
        "marca",
        "modelo",
        "serie",
        "ubicacion",
        "estado",
        "criticidad"
    ]

    faltantes = [c for c in columnas if c not in df.columns]

    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Faltan columnas: {faltantes}"
        )

    creados = 0
    errores = []
    inventarios_archivo = set()

    for i, row in df.iterrows():
        try:
            # Buscar empresa
            empresa = db.query(Empresa).filter(
                Empresa.nombre.ilike(row["empresa"])
            ).first()

            if not empresa:
                raise Exception("Empresa no encontrada")

            # Buscar sede
            sede = db.query(Sede).filter(
                Sede.nombre.ilike(row["sede"]),
                Sede.empresa_id == empresa.id
            ).first()

            if not sede:
                raise Exception("Sede no encontrada")

            # Buscar categoría (opcional)
            categoria = None
            if row["categoria"]:
                categoria = db.query(Categoria).filter(
                    Categoria.nombre.ilike(row["categoria"])
                ).first()

            # Validar estado y criticidad
            estado = str(row["estado"]).upper()
            criticidad = str(row["criticidad"]).upper()

            validar_estado_y_criticidad(estado, criticidad)

            numero_inventario = normalizar_numero_inventario(
                row.get("inventario") if "inventario" in df.columns else None
            )
            if numero_inventario:
                clave_inventario = numero_inventario.lower()
                if clave_inventario in inventarios_archivo:
                    raise Exception(
                        "Equipo ya existe: número de inventario repetido en el archivo"
                    )
                numero_inventario = validar_numero_inventario(
                    db,
                    numero_inventario,
                )
                inventarios_archivo.add(clave_inventario)

            # Crear equipo
            nuevo = Equipo(
                nombre=row["nombre"],
                empresa_id=empresa.id,
                sede_id=sede.id,
                categoria_id=categoria.id if categoria else None,
                marca=row["marca"],
                modelo=row["modelo"],
                serie=row["serie"],
                ubicacion=row["ubicacion"],
                codigo_id=row["codigo_inventario"],
                inventario=numero_inventario,
                estado=estado,
                criticidad=criticidad,
                activo=True
            )

            db.add(nuevo)
            creados += 1

        except Exception as e:
            errores.append({
                "fila": int(i + 2),
                "error": str(e)
            })

    db.commit()

    return {
        "creados": creados,
        "errores": errores
    }
