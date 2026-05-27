// ============================================================
// API - SCHEDULER INTELIGENTE PRO
// Archivo: frontend/src/api/schedulerInteligenteApi.js
// ============================================================

import api from "./axios";

const BASE = "/scheduler-inteligente";

export const schedulerInteligenteApi = {
  inicializar: () => api.post(`${BASE}/inicializar`),
  dashboard: () => api.get(`${BASE}/dashboard`),
  listarReglas: () => api.get(`${BASE}/reglas`),
  crearRegla: (payload) => api.post(`${BASE}/reglas`, payload),
  actualizarRegla: (id, payload) => api.put(`${BASE}/reglas/${id}`, payload),
  eliminarRegla: (id) => api.delete(`${BASE}/reglas/${id}`),
  ejecutarAhora: () => api.post(`${BASE}/ejecutar`),
  listarSugerencias: (estado = "") => api.get(`${BASE}/sugerencias${estado ? `?estado=${estado}` : ""}`),
  aprobarSugerencia: (id) => api.post(`${BASE}/sugerencias/${id}/aprobar`),
  rechazarSugerencia: (id) => api.post(`${BASE}/sugerencias/${id}/rechazar`),
  logs: () => api.get(`${BASE}/logs`),
};

export default schedulerInteligenteApi;
