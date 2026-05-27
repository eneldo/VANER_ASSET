// ============================================================
// API: Logs Inteligentes SaaS PRO
// Archivo: frontend/src/api/logsInteligentesApi.js
// FASE 34.2.5
// ============================================================

import api from "./axios";

const BASE = "/logs-inteligentes";

export async function getLogsResumen() {
  const { data } = await api.get(`${BASE}/resumen`);
  return data;
}

export async function getLogs(params = {}) {
  const { data } = await api.get(`${BASE}/`, { params });
  return data;
}

export async function crearLogDemo() {
  const { data } = await api.post(`${BASE}/demo`);
  return data;
}

export async function limpiarLogs(dias = 30) {
  const { data } = await api.delete(`${BASE}/limpiar`, { params: { dias } });
  return data;
}

export function getLogsExportUrl(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const baseURL = api.defaults.baseURL || "";
  return `${baseURL}${BASE}/exportar.csv${qs ? `?${qs}` : ""}`;
}
