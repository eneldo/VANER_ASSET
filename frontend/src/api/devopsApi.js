// ============================================================
// API: DevOps SaaS PRO
// Archivo: frontend/src/api/devopsApi.js
// FASE 34.2.6
// ============================================================

import api from "./axios";

export async function obtenerEstadoDevOps() {
  const { data } = await api.get("/devops/estado");
  return data;
}

export async function obtenerLogsServicio(servicio, lineas = 80) {
  const { data } = await api.get(`/devops/logs/${servicio}`, {
    params: { lineas },
  });
  return data;
}

export async function ejecutarAccionDevOps(servicio, accion) {
  const { data } = await api.post("/devops/accion", {
    servicio,
    accion,
  });
  return data;
}
