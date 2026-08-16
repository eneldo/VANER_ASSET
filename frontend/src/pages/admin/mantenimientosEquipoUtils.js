export const UBICACION_SIN_REGISTRO = "__SIN_UBICACION__";

function limpiarValor(value) {
  return String(value || "").trim();
}

function normalizarBusqueda(value) {
  return limpiarValor(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("es");
}

export function obtenerValorUbicacionEquipo(equipo = {}) {
  return limpiarValor(equipo.ubicacion) || UBICACION_SIN_REGISTRO;
}

export function obtenerEtiquetaUbicacionEquipo(value) {
  return value === UBICACION_SIN_REGISTRO ? "Sin ubicación registrada" : value;
}

export function construirEtiquetaEquipo(equipo = {}) {
  const nombre = limpiarValor(equipo.nombre) || "Equipo sin nombre";
  const ubicacion = obtenerEtiquetaUbicacionEquipo(obtenerValorUbicacionEquipo(equipo));
  const partes = [nombre, `Ubicación: ${ubicacion}`];
  const inventario = limpiarValor(equipo.inventario);
  const codigo = limpiarValor(equipo.codigo_id || equipo.codigo);
  const serie = limpiarValor(equipo.serie);

  if (inventario) partes.push(`Inv: ${inventario}`);
  if (codigo) partes.push(`Código: ${codigo}`);
  if (serie) partes.push(`Serie: ${serie}`);

  return partes.join(" · ");
}

export function listarUbicacionesEquipos(equipos = [], sedeId) {
  if (!sedeId) return [];

  const ubicaciones = new Map();

  equipos
    .filter((equipo) => String(equipo.sede_id) === String(sedeId))
    .forEach((equipo) => {
      const value = obtenerValorUbicacionEquipo(equipo);
      const key = normalizarBusqueda(value);

      if (!ubicaciones.has(key)) {
        ubicaciones.set(key, {
          value,
          label: obtenerEtiquetaUbicacionEquipo(value),
        });
      }
    });

  return [...ubicaciones.values()].sort((primera, segunda) =>
    primera.label.localeCompare(segunda.label, "es", { sensitivity: "base" })
  );
}

export function encontrarUbicacionDisponible(ubicaciones = [], busqueda = "") {
  const termino = normalizarBusqueda(busqueda);
  if (!termino) return null;

  return (
    ubicaciones.find(
      (ubicacion) =>
        normalizarBusqueda(ubicacion.value) === termino ||
        normalizarBusqueda(ubicacion.label) === termino
    ) || null
  );
}

export function filtrarEquiposPorUbicacion(equipos = [], sedeId, ubicacion) {
  if (!sedeId || !ubicacion) return [];

  return equipos
    .filter(
      (equipo) =>
        String(equipo.sede_id) === String(sedeId) &&
        normalizarBusqueda(obtenerValorUbicacionEquipo(equipo)) ===
          normalizarBusqueda(ubicacion)
    )
    .sort((primero, segundo) =>
      construirEtiquetaEquipo(primero).localeCompare(construirEtiquetaEquipo(segundo), "es", {
        sensitivity: "base",
      })
    );
}
