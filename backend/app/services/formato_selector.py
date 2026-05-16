# ============================================================
# SERVICIO: SELECTOR DE FORMATO DINÁMICO
# Archivo: backend/app/services/formato_selector.py
# ============================================================
# Convierte nombres reales de equipos/categorías en el código del formato.
# Ejemplo: "planta eléctrica Caterpillar" -> PLANTA_ELECTRICA
# ============================================================

import unicodedata


def normalizar_texto(texto: str) -> str:
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.upper().strip()


def seleccionar_codigo_formato(*valores: str) -> str:
    """
    Recibe nombre equipo, categoría, tipo u otra descripción y retorna
    el código técnico del formato más adecuado.
    """

    texto = normalizar_texto(" ".join([v or "" for v in valores]))

    reglas = [
        ("ASCENSOR", ["ASCENSOR", "ELEVADOR"]),
        ("PLANTA_ELECTRICA", ["PLANTA ELECTRICA", "GENERADOR", "GRUPO ELECTROGENO"]),
        ("RED_INCENDIO", ["RED CONTRA INCENDIO", "INCENDIO", "PCI", "BOMBA JOCKEY", "DETECTOR HUMO"]),
        ("BASCULA", ["BASCULA", "BALANZA", "PESAJE"]),
        ("TABLERO_ELECTRICO", ["TABLERO", "TABLERO ELECTRICO", "BREAKER", "SUBESTACION"]),
        ("CCTV", ["CCTV", "CAMARA", "VIDEOVIGILANCIA", "NVR", "DVR"]),
        ("NEVERA_INDUSTRIAL", ["NEVERA", "REFRIGERADOR", "REFRIGERACION"]),
        ("CONGELADOR", ["CONGELADOR", "FREEZER", "ULTRACONGELADOR"]),
        ("BOMBA_AGUA", ["BOMBA", "BOMBA DE AGUA", "HIDRAULICA", "MOTOBOMBA"]),
        ("VENTILADOR_INDUSTRIAL", ["VENTILADOR", "EXTRACTOR", "AIRFLOW", "SOPLADOR"]),
        ("LLAMADO_ENFERMERIA", ["LLAMADO ENFERMERIA", "ENFERMERIA", "PULSADOR", "TIMBRE HOSPITALARIO"]),
        ("AIRE_ACONDICIONADO", ["AIRE", "MINISPLIT", "HVAC", "CHILLER", "MANEJADORA"]),
        ("UPS", ["UPS", "BATERIA", "SISTEMA ININTERRUMPIDO"]),
    ]

    for codigo, palabras in reglas:
        if any(p in texto for p in palabras):
            return codigo

    return "INDUSTRIAL_GENERAL"
