from datetime import datetime

from fastapi import HTTPException


def validar_mantenimiento_editable(mantenimiento):
    if str(getattr(mantenimiento, "estado", "") or "").upper() == "FINALIZADO":
        raise HTTPException(
            status_code=409,
            detail={
                "codigo": "OT_FINALIZADA",
                "mensaje": "El mantenimiento está finalizado. Un coordinador o administrador debe reabrirlo antes de modificar acciones o evidencias.",
            },
        )


def aplicar_reapertura(mantenimiento):
    estado_anterior = str(getattr(mantenimiento, "estado", "") or "").upper()
    if estado_anterior != "FINALIZADO":
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden reabrir mantenimientos finalizados.",
        )

    ahora = datetime.now()
    mantenimiento.estado = "EN_PROCESO"
    mantenimiento.fecha_finalizacion = None
    mantenimiento.fecha_fin = None
    mantenimiento.fecha_pausa = None
    mantenimiento.fecha_inicio = mantenimiento.fecha_inicio or ahora
    mantenimiento.cerrado = False
    mantenimiento.fecha_cierre = None
    mantenimiento.actualizado_en = ahora
    mantenimiento.updated_at = ahora
    return estado_anterior
