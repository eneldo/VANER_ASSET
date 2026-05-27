# ============================================================
# BI EJECUTIVO SCHEMAS
# Archivo: backend/app/schemas/bi_schema.py
# ============================================================

from pydantic import BaseModel
from typing import List, Optional


# ============================================================
# KPI GENERALES
# ============================================================

class BIKPIResponse(BaseModel):

    total_empresas: int
    total_sedes: int
    total_equipos: int
    total_mantenimientos: int
    total_usuarios: int


# ============================================================
# MANTENIMIENTOS POR ESTADO
# ============================================================

class BIMantenimientoEstado(BaseModel):

    estado: str
    total: int


# ============================================================
# EQUIPOS POR EMPRESA
# ============================================================

class BIEquiposEmpresa(BaseModel):

    empresa: str
    equipos: int


# ============================================================
# COSTOS POR EMPRESA
# ============================================================

class BICostosEmpresa(BaseModel):

    empresa: str
    costo_total: float


# ============================================================
# COSTOS POR SEDE
# ============================================================

class BICostosSede(BaseModel):

    sede: str
    costo_total: float


# ============================================================
# TÉCNICOS PRODUCTIVOS
# ============================================================

class BITecnicoProductividad(BaseModel):

    tecnico: str
    mantenimientos: int


# ============================================================
# EQUIPOS CRÍTICOS
# ============================================================

class BIEquipoCritico(BaseModel):

    equipo: str
    empresa: str
    mantenimientos: int


# ============================================================
# RESPUESTA DASHBOARD GENERAL
# ============================================================

class BIDashboardResponse(BaseModel):

    kpis: BIKPIResponse

    mantenimientos_estados: List[
        BIMantenimientoEstado
    ]

    equipos_empresa: List[
        BIEquiposEmpresa
    ]

    costos_empresa: Optional[
        List[BICostosEmpresa]
    ] = []

    costos_sede: Optional[
        List[BICostosSede]
    ] = []

    tecnicos_productivos: Optional[
        List[BITecnicoProductividad]
    ] = []

    equipos_criticos: Optional[
        List[BIEquipoCritico]
    ] = []