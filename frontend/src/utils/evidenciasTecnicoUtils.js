export const MAX_EVIDENCIAS_POR_ETAPA = 4;

const TIPOS_ETAPA = new Set(["ANTES", "DURANTE", "DESPUES"]);
const ETIQUETAS_ETAPA = {
  ANTES: "Antes",
  DURANTE: "Durante",
  DESPUES: "Después",
};

function normalizarTipo(tipo) {
  return String(tipo || "").trim().toUpperCase();
}

export function contarEvidenciasPorTipo(evidencias, tipo) {
  const tipoNormalizado = normalizarTipo(tipo);
  return (Array.isArray(evidencias) ? evidencias : []).filter(
    (evidencia) => normalizarTipo(evidencia?.tipo) === tipoNormalizado
  ).length;
}

export function obtenerCuposEvidencia(evidencias, tipo) {
  const tipoNormalizado = normalizarTipo(tipo);
  if (!TIPOS_ETAPA.has(tipoNormalizado)) return null;

  return Math.max(
    0,
    MAX_EVIDENCIAS_POR_ETAPA - contarEvidenciasPorTipo(evidencias, tipoNormalizado)
  );
}

export function validarSeleccionEvidencias(archivos, evidencias, tipo) {
  const seleccionados = Array.from(archivos || []);
  const tipoNormalizado = normalizarTipo(tipo);
  const cupos = obtenerCuposEvidencia(evidencias, tipoNormalizado);

  if (cupos === null) return { archivos: seleccionados, error: "" };

  const etiqueta = ETIQUETAS_ETAPA[tipoNormalizado] || tipoNormalizado;
  if (cupos === 0) {
    return {
      archivos: [],
      error: "Ya alcanzaste el máximo de " + MAX_EVIDENCIAS_POR_ETAPA + " evidencias para " + etiqueta + ".",
    };
  }
  if (seleccionados.length > cupos) {
    return {
      archivos: [],
      error: "Puedes seleccionar máximo " + cupos + " archivo(s) más para " + etiqueta + ".",
    };
  }

  return { archivos: seleccionados, error: "" };
}
