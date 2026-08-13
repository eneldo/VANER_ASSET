const ETIQUETAS_CAMPOS = {
  nombre: "Nombre de empresa",
  nit: "NIT",
  telefono: "Telefono",
  direccion: "Direccion",
  correo: "Correo corporativo",
  logo_url: "Logo URL",
  activo: "Estado",
};

const campoOpcional = (valor) => valor?.trim() || null;

export const construirPayloadEmpresa = (form) => ({
  ...form,
  nombre: form.nombre.trim(),
  nit: campoOpcional(form.nit),
  telefono: campoOpcional(form.telefono),
  direccion: campoOpcional(form.direccion),
  correo: campoOpcional(form.correo),
  logo_url: campoOpcional(form.logo_url),
});

export const obtenerMensajeError = (error, mensajePredeterminado) => {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

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

    if (mensajes.length > 0) return mensajes.join("\n");
  }

  return mensajePredeterminado;
};
