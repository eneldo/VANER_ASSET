// ============================================================
// API: FORMATOS Y BITÁCORAS DINÁMICAS PRO
// Archivo: frontend/src/api/formatosDinamicosApi.js
// ============================================================

import API from "./axios";

export const formatosDinamicosApi = {
  listarFormatos: () => API.get("/formatos-dinamicos/"),
  obtenerFormatoPorCodigo: (codigo) => API.get(`/formatos-dinamicos/codigo/${codigo}`),
  obtenerBitacoraMantenimiento: (mantenimientoId) =>
    API.get(`/bitacoras-dinamicas/mantenimiento/${mantenimientoId}`),
  guardarBitacora: (payload) => API.post("/bitacoras-dinamicas/guardar", payload),
  historialEquipo: (equipoId) => API.get(`/bitacoras-dinamicas/historial/equipo/${equipoId}`),
};

export default formatosDinamicosApi;
