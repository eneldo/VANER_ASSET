// ============================================================
// API: Backups Inteligentes SaaS PRO
// Archivo: frontend/src/api/backupsApi.js
// ============================================================

import api from "./axios";

const BASE = "/backups-inteligentes";

export async function getBackupsStatus() {
  const { data } = await api.get(`${BASE}/status`);
  return data;
}

export async function listarBackups(limit = 50) {
  const { data } = await api.get(`${BASE}/`, { params: { limit } });
  return data;
}

export async function ejecutarBackup(payload) {
  const { data } = await api.post(`${BASE}/ejecutar`, payload);
  return data;
}

export async function limpiarBackups(retencionDias = 15) {
  const { data } = await api.delete(`${BASE}/limpiar`, {
    params: { retencion_dias: retencionDias },
  });
  return data;
}

export function urlDescargarBackup(id) {
  const apiBase = import.meta.env.VITE_API_URL || "";
  return `${apiBase}${BASE}/${id}/descargar`;
}
