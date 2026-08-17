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

const ETIQUETAS_CAMPOS = {
  fecha: 'Fecha',
  mantenimiento_id: 'Mantenimiento',
  tecnico_id: 'Tecnico',
  numero_ot: 'Numero de OT',
  firma_usuario: 'Firma del cliente / usuario',
  firma_operario: 'Firma del tecnico / operario',
  firma_coordinador: 'Firma del gerente / coordinador',
};

export function construirPayloadFormato(form, mantenimientoId, templateKey, template) {
  return {
    ...form,
    mantenimiento_id: String(mantenimientoId),
    tecnico_id: form.tecnico_id || null,
    fecha: form.fecha || null,
    tipo_equipo: form.tipo_equipo || templateKey,
    trabajos_realizados: {
      ...form.trabajos_realizados,
      _plantilla: templateKey,
      _titulo_plantilla: template.titulo,
    },
  };
}

export function obtenerMensajeErrorFormato(error, mensajePredeterminado) {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === 'string') return detalle;

  if (Array.isArray(detalle)) {
    const mensajes = detalle
      .map((item) => {
        const campo = item?.loc?.at(-1);
        const etiqueta = ETIQUETAS_CAMPOS[campo] || campo;
        const mensaje = item?.msg;

        if (!mensaje) return null;
        return etiqueta ? `${etiqueta}: ${mensaje}` : mensaje;
      })
      .filter(Boolean);

    if (mensajes.length > 0) return mensajes.join('\n');
  }

  if (detalle && typeof detalle === 'object') {
    return detalle.mensaje || detalle.message || detalle.msg || mensajePredeterminado;
  }

  return mensajePredeterminado;
}
