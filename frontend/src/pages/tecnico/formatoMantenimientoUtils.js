export function extraerEquipoAsignado(detalle = {}) {
  const equipo = detalle?.equipo_basico || {};
  const encabezado = detalle?.encabezado || {};
  const tecnico = detalle?.tecnico || {};

  return {
    id: equipo.id || '',
    nombre: equipo.nombre || '',
    categoria: equipo.categoria || '',
    inventario: equipo.inventario || '',
    codigo_id: equipo.codigo_id || '',
    marca: equipo.marca || '',
    modelo: equipo.modelo || '',
    serie: equipo.serie || '',
    ubicacion: equipo.ubicacion || encabezado.sede_nombre || '',
    invima: equipo.invima || '',
    criticidad: equipo.criticidad || '',
    estado: equipo.estado || '',
    empresa_nombre: encabezado.empresa_nombre || '',
    sede_nombre: encabezado.sede_nombre || '',
    tecnico_nombre: tecnico.nombre_completo || '',
  };
}


export function construirPrefillFormato(detalle, mantenimientoId, previo = {}) {
  const equipo = extraerEquipoAsignado(detalle);
  const mantenimiento = detalle?.mantenimiento || {};

  return {
    ...previo,
    mantenimiento_id: String(mantenimientoId),
    numero_ot: mantenimiento.id || previo.numero_ot || '',
    numero_inventario:
      equipo.inventario || equipo.codigo_id || equipo.serie || previo.numero_inventario || '',
    ubicacion: equipo.ubicacion || previo.ubicacion || '',
    tecnico_nombre: equipo.tecnico_nombre || previo.tecnico_nombre || '',
    mantenimiento_tipo:
      mantenimiento.tipo || previo.mantenimiento_tipo || 'Preventivo',
    tipo_equipo:
      previo.tipo_equipo || equipo.nombre || equipo.categoria || '',
  };
}
